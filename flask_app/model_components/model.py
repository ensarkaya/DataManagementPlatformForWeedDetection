import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
from torchvision.models import ResNet34_Weights, ResNet18_Weights
class DoubleConv(nn.Module):
    """(convolution => [BN] => ReLU) * 2"""

    def __init__(self, in_channels, out_channels, mid_channels=None):
        super().__init__()
        if not mid_channels:
            mid_channels = out_channels
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, mid_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(mid_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)


class Down(nn.Module):
    """Downscaling with maxpool then double conv"""

    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_channels, out_channels)
        )

    def forward(self, x):
        return self.maxpool_conv(x)

class OutConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(OutConv, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        return self.conv(x)
    
class Up(nn.Module):  
    """Upscaling then double conv"""  
  
    def __init__(self, in_channels, out_channels, skip_channels, upsample_mode='bilinear'):  
        super().__init__()  
  
        if upsample_mode == 'bilinear':  
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)  
        elif upsample_mode == 'conv_transpose':  
            self.up = nn.ConvTranspose2d(in_channels , in_channels, kernel_size=2, stride=2)  
        else:  
            raise ValueError(f"Unsupported upsample_mode: {upsample_mode}")  
  
        # The total number of channels is the sum of skip_channels and in_channels  
        self.conv = DoubleConv(in_channels + skip_channels, out_channels, mid_channels=out_channels)  
  
    def forward(self, x1, x2):  
        x1 = self.up(x1)  
        # input is CHW  
        diffY = x2.size()[2] - x1.size()[2]  
        diffX = x2.size()[3] - x1.size()[3]  
  
        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,  
                        diffY // 2, diffY - diffY // 2])  
        x = torch.cat([x2, x1], dim=1)  

        return self.conv(x)  

    
class ResNetUNet(nn.Module):
    def __init__(self, n_classes, resnet_model='resnet34', resnet_model_path=None):
        super().__init__()

        # Use a pre-trained ResNet model as the encoder
        if resnet_model == 'resnet18':
            # Specify the weights to use if weights_path is not provided
            weights = ResNet18_Weights.IMAGENET1K_V1 if not resnet_model_path else None
            self.base_model = models.resnet18(weights=weights)
        elif resnet_model == 'resnet34':
            # Specify the weights to use if weights_path is not provided
            weights = ResNet34_Weights.IMAGENET1K_V1 if not resnet_model_path else None
            self.base_model = models.resnet34(weights=weights)
        else:
            raise ValueError(f"Unsupported ResNet model: {resnet_model}")

        # If a weights_path is provided, load the weights from the local file
        if resnet_model_path:
            self.base_model.load_state_dict(torch.load(resnet_model_path))

        
        self.base_layers = list(self.base_model.children())

        # Encoder layers
        self.layer0 = nn.Sequential(*self.base_layers[:3]) # size=(N, 64, x.H/2, x.W/2)
        self.layer1 = nn.Sequential(*self.base_layers[3:5]) # size=(N, 64, x.H/4, x.W/4)
        self.layer2 = self.base_layers[5]  # size=(N, 128, x.H/8, x.W/8)
        self.layer3 = self.base_layers[6]  # size=(N, 256, x.H/16, x.W/16)
        self.layer4 = self.base_layers[7]  # size=(N, 512, x.H/32, x.W/32)

        # Decoder layers and Up-sampling      
        self.up1 = Up(512, 256, 256, upsample_mode='bilinear')  # Decoder for layer4        
        self.up2 = Up(256, 128, 128, upsample_mode='bilinear')  # Decoder for layer3        
        self.up3 = Up(128, 64, 64, upsample_mode='bilinear')   # Decoder for layer2        
        self.up4 = Up(64, 64, 64, upsample_mode='bilinear')     # Decoder for layer1  
        self.up5 = Up(64, 32, 64, upsample_mode='conv_transpose')


        # Final convolution
        self.outc = OutConv(32, n_classes)

    def forward(self, x):  
        x0 = self.layer0(x)    
        x1 = self.layer1(x0)   
        x2 = self.layer2(x1)   
        x3 = self.layer3(x2)   
        x4 = self.layer4(x3)   

        x = self.up1(x4, x3)  
        x = self.up2(x, x2)  
        x = self.up3(x, x1)  
        x = self.up4(x, x0)  
        x = self.up5(x, x0)

        x = F.interpolate(x, size=(256, 256), mode='bilinear', align_corners=True)

        logits = self.outc(x)  

        return logits
