import React, { useState, useEffect } from 'react';
import { List, Card, Spin, Image, Pagination, Space, Row , Col} from 'antd';
import { useGetGeneratedImagesForUAVFlightQuery, useUavFlightsWithCompletedAnalysisQuery } from '../../store/aiAnalysisApi';
import { useAppSelector } from '../../store/hooks';
import moment from 'moment';

const AIAnalysisPage = () => {
  const auth = useAppSelector((state) => state.auth);
  const [selectedFlightId, setSelectedFlightId] = useState<number | null>(null);
  const pageSize = 6; 
  const imagesPerPage = 3;

  const [currentImagePage, setCurrentImagePage] = useState<number>(1);

  const { data: flightsWithAnalysis, isLoading: isLoadingFlights, refetch } = useUavFlightsWithCompletedAnalysisQuery(auth.userId);

  const { data: generatedImages, isLoading: isLoadingImages, refetch:refetchImages } = useGetGeneratedImagesForUAVFlightQuery(selectedFlightId, {
    skip: selectedFlightId === null,
  });

  useEffect(() => {
    refetch();
  }, [refetch]);

  const handleSelectFlight = (flightId: number) => {
    if(!selectedFlightId || flightId !== selectedFlightId) {
      setCurrentImagePage(1);
    }
    setSelectedFlightId(flightId);    
    };

  const handleImagePageChange = (page: number): void  => {
    setCurrentImagePage(page);
  };

  const getCurrentPageImages = (images: any[]): string[]  => {
    const startIndex = (currentImagePage - 1) * imagesPerPage;
    return images.slice(startIndex, startIndex + imagesPerPage);
  };

  if (isLoadingFlights) return <Spin tip="Loading flights..."></Spin>;

  function ResultDataDisplay({ resultData }: { resultData: { weeds?: number; sorghum?: number; background?: number } }) {
    const formatNumber = (num: number) => num.toFixed(2);
    return (
      <div>
        {resultData.weeds  && <p>Weeds: {formatNumber(resultData.weeds)}%</p>}
        {resultData.sorghum  && <p>Sorghum: {formatNumber(resultData.sorghum)}%</p>}
      </div>
    );
  }
  
  return (
    <div>
      <List
        grid={{ gutter: 16, column: 3 }}
        dataSource={flightsWithAnalysis || []}
        pagination={{
          pageSize: pageSize,
          position: "bottom",
        }}
        renderItem={(flight: any) => (
          <List.Item key={flight.id}>
            <Card
              title={`${moment(flight.flight_date).format('YYYY-MM-DD')} - ${flight.description}`}
              onClick={() => handleSelectFlight(flight.id)}
              style={{
                width: flight.id === selectedFlightId ? 500 : 300
                  ,
                  margin: "16px 0",
                cursor: "pointer",
                border:
                  flight.id === selectedFlightId
                    ? "2px solid blue"
                    : "1px solid #f0f0f0",
              }}
            >
              {flight.id === selectedFlightId && (
                <Space direction="vertical" style={{ width: '100%' }}>
                  {isLoadingImages ? (
                    <Spin tip="Loading analysis results..."></Spin>
                  ) : (
                    <>
                    <Row gutter={[16, 16]}>
                      {getCurrentPageImages(generatedImages || []).map((image: any, index: number) => (
                        <Col span={12} key={image.id + '_col_' + index} style={{ marginBottom: 16 }}>
                          <Card
                            bodyStyle={{ padding: 0 }}
                            bordered={false}
                            style={{ boxShadow: '0 4px 8px 0 rgba(0,0,0,0.2)' }}
                          >
                            <Image
                              key={image.id + '_original_' + index}
                              width="100%"
                              src={`http://10.154.6.34:8000${image.image_details.resized_image}`}
                              alt={`"Original Image" ${index}`}
                              style={{ marginBottom: 8 }}
                            />
                            <Image
                              key={image.id + '_processed_' + index}
                              width="100%"
                              src={`http://10.154.6.34:8000${image.generated_image}`}
                              alt={`"Processed Image" ${index}`}
                              style={{ marginBottom: 8 }}
                            />
                            <div style={{ padding: '8px 16px' }}>
                              <ResultDataDisplay resultData={image.result_data} />
                            </div>
                          </Card>
                        </Col>
                      ))}
                        {generatedImages && generatedImages.length % 2 !== 0 && (
                          <Col span={12}></Col>
                        )}
                    </Row>
                      <Pagination
                        simple
                        current={currentImagePage}
                        onChange={handleImagePageChange}
                        total={(generatedImages || []).length}
                        pageSize={imagesPerPage}
                        showSizeChanger={false}
                      />
                    </>
                  )}
                </Space>
              )}
            </Card>
          </List.Item>
        )}
      />

    </div>
  );
};

export default AIAnalysisPage;
