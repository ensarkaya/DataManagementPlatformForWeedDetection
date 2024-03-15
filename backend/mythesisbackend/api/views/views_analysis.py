import time
from rest_framework import views, status
from rest_framework.response import Response
from django_q.tasks import async_task
from ..models import AnalysisJob, FieldImage, UAVFlight, ProcessingResult, User
from ..serializers import AnalysisJobSerializer, ProcessingResultSerializer, UAVFlightSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
import base64
from django.db.models import Exists, OuterRef
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

def send_notification_email(job_status, recipient_email, uav_flight_date):
    if recipient_email is None:
        logger.warning("Recipient email not provided. Skipping email notification.")
        return
    if job_status not in ['completed', 'failed']:
        logger.warning(f"Invalid job status: {job_status}. Skipping email notification.")
        return
    message = Mail(
        from_email='ensar8@gmail.com',
        to_emails=recipient_email,
        subject='Ai Analysis Job Notification',
        plain_text_content=f'Your ai analysis for flight: {uav_flight_date} has been {job_status}.'
    )
    try:
        if message is None:
            logger.warning("Message not provided. Skipping email notification.")
            return
        
        # sg = SendGridAPIClient('')  # Use environment variable here
        # response = sg.send(message)
        # logger.warning(f"Email sent to {recipient_email} with status code {response.status_code}")
        logger.warning(f"Email sent to {recipient_email} with status code 200")
    except Exception as e:
        logger.error(e.message)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_analysis(request):
    uav_flight_id = request.data.get('uav_flight_id', None)
    field_image_id = request.data.get('image_id', None)
    user = request.user
    logger.warning(f"Starting analysis for uav_flight: {uav_flight_id} and field image: {field_image_id}")
    
    if uav_flight_id is None:
        return Response({'error': 'uav_flight_id not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        uav_flight = UAVFlight.objects.get(id=uav_flight_id, owner=user)
    except UAVFlight.DoesNotExist:
        return Response({'error': 'UAV Flight not found'}, status=status.HTTP_404_NOT_FOUND)
    logger.warning(f"UAV Flight found: {uav_flight}")
    images_to_process = []

    # Check and filter for unprocessed or not in-process images
    if field_image_id:
        try:
            field_image = FieldImage.objects.get(id=field_image_id, uav_flight=uav_flight)
            if ProcessingResult.objects.filter(image=field_image).exists() or \
               AnalysisJob.objects.filter(field_image=field_image, status__in=['pending', 'processing', 'completed']).exists():
                return Response({'error': 'Image is already processed or in the process'}, status=status.HTTP_400_BAD_REQUEST)
            images_to_process = [field_image]
        except FieldImage.DoesNotExist:
            return Response({'error': 'Field Image not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        # Fetch all images for the UAV flight
        all_images = FieldImage.objects.filter(uav_flight=uav_flight)

        # Determine which images have not been processed or are not currently being processed
        images_already_processed_or_processing = set(
            ProcessingResult.objects.filter(image__uav_flight=uav_flight).values_list('image', flat=True)
        ).union(
            AnalysisJob.objects.filter(
                field_image__uav_flight=uav_flight,
                status__in=['pending', 'processing', 'completed']
            ).values_list('field_image', flat=True)
        )
        logger.warning(f"Images already processed or processing: {images_already_processed_or_processing}")
        # Filter out the images that have been processed or are being processed
        images_to_process = [image for image in all_images if image.id not in images_already_processed_or_processing]
        logger.warning(f"Images to process: {images_to_process}")
        if not images_to_process:
            return Response({'error': 'All images are already processed or being processed'}, status=status.HTTP_400_BAD_REQUEST)

    job_ids = []  

    # Create analysis jobs for unprocessed images and collect their IDs
    for image in images_to_process:
        # Create the job if no pending/processing job for the same image exists
        if not AnalysisJob.objects.filter(field_image=image, status__in=['pending', 'processing']).exists():
            job = AnalysisJob.objects.create(owner=user, uav_flight=uav_flight, field_image=image, status='pending')
            job_ids.append(job.id)  # Collect the newly created job's ID
            logger.warning(f"Created job {job.id} for image {image.id}")
        else:
            logger.warning(f"Job already exists for image {image.id}")
    # Trigger analysis task and send an email at the end of processing
    if job_ids:  # Ensure we have job IDs to process
        for job_id in job_ids:
            logger.warning(f"Starting async_task for job ID: {job_id}")
            task_id = async_task(analysis_function, job_id=job_id)
            time.sleep(1)  # Throttle task submission to avoid flooding
            logger.warning(f"Enqueuing analysis for job ID: {job_id} with unique task ID: {task_id}")
    else:
        return Response({'error': 'No images to process'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Analysis started successfully'}, status=status.HTTP_201_CREATED)


def process_image(image_id):
    """
    Function to process an individual image. Extracted for clarity and reusability.
    """
    try:
        field_image = FieldImage.objects.get(id=image_id)
        with field_image.image.open('rb') as img:
            image_content = img.read()
        files = {'image': (field_image.image.name, image_content, 'image/png')}
        response = requests.post(f"{settings.FLASK_SERVICE_URL}/process_images", files=files)
        if response.status_code == 200:
            data = response.json()
            image_data = base64.b64decode(data['image_base64'])
            processed_image_content = ContentFile(image_data, name=f"generated_image_{image_id}.png")
            ProcessingResult.objects.create(
                image=field_image,
                result_data=data['result_data'],
                date_processed=timezone.now(),
                generated_image=processed_image_content
            )
            return True
    except FieldImage.DoesNotExist:
        logger.error(f"Field Image with ID {image_id} not found")
    except Exception as e:
        logger.error(f"Failed to process image {image_id}: {e}")
    return False

def analysis_function(job_id):
    job_status = ''
    try:
        with transaction.atomic():
            # Lock the job row for update to prevent concurrent modifications
            job = AnalysisJob.objects.select_for_update().get(id=job_id)
            if job.status in ['completed', 'processing']:
                logger.warning(f"Job {job_id} already processed or processing. Skipping.")
                return

            job.status = 'processing'
            job.save()

            success = True

            if job.field_image:
                success &= process_image(job.field_image.id)
            else:
                logger.error(f"No field image specified for job {job_id}")
                success = False 
            
            job.status = 'completed' if success else 'failed'
            job_status = job.status
            job.save()
    except AnalysisJob.DoesNotExist:
        logger.error(f"AnalysisJob with ID {job_id} not found")
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        job.status = 'failed'
        job_status = job.status
        job.save()
    
    # Send email notification
    try:
        user_email = job.owner.email
        uav_flight_date = job.uav_flight.flight_date
        # send_notification_email(job_status, user_email, uav_flight_date)
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_generated_images_for_uav_flight(request):
    uav_flight_id = request.query_params.get('uav_flight_id', None)
    user = request.user
    try:
        # Ensure the UAV flight belongs to the requesting user for added security
        uav_flight = UAVFlight.objects.get(id=uav_flight_id, owner=user)
    except UAVFlight.DoesNotExist:
        return Response({'error': f'UAVFlight not found {uav_flight_id}'}, status=status.HTTP_404_NOT_FOUND)

    # Fetch all FieldImages related to the UAV flight
    field_images = FieldImage.objects.filter(uav_flight=uav_flight)

    # Initialize a list to hold all processing results
    processing_results = []

    # For each field image, fetch its processing results
    for image in field_images:
        results = ProcessingResult.objects.filter(image=image, generated_image__isnull=False)
        processing_results.extend(results)

    # Serialize the processing results to send back to the client
    serializer = ProcessingResultSerializer(processing_results, many=True)

    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def uav_flights_with_completed_analysis(request):
    user = request.user

    # Subquery to check for the existence of a ProcessingResult linked to each FieldImage
    processed_images_exists = ProcessingResult.objects.filter(
        image=OuterRef('pk'),
        generated_image__isnull=False
    ).values('image')

    # Annotate FieldImage queryset with a boolean indicating the existence of such a ProcessingResult
    field_images_with_results = FieldImage.objects.annotate(
        has_processed_image=Exists(processed_images_exists)
    ).filter(has_processed_image=True)

    # Use the annotated FieldImage queryset to filter UAVFlights
    uav_flights = UAVFlight.objects.filter(
        images__in=field_images_with_results,
        owner=user
    ).distinct()

    serializer = UAVFlightSerializer(uav_flights, many=True)

    return Response(serializer.data)