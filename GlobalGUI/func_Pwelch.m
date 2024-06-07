function [salida] = func_Pwelch(Data_1)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
load('Noise_1000000_1s.mat');
DataNoise=Dev1_3.Dev1_ai0;
fsample=1000000;
winnum=8500;
% Mean_Filter=100;
% Exponent = 3;
% to adjust
 cutoff_frequency_min=70;
 cutoff_frequency_max =10000;

%  nfft=fsample; %Just one second of Data
window= hamming(winnum);
% hold on
[Welch_PSD,f_PSD]=pwelch(Data_1,window,winnum/2,winnum,fsample);
[Welch_PSD_noise,f_PSD_noise]=pwelch(DataNoise,window,winnum/2,winnum,fsample);

% Moments
% Calculate first moment
 idxb = find(f_PSD > cutoff_frequency_min);
 idxf = find(f_PSD < cutoff_frequency_max);
 idxb=idxb(1);
 idxf=idxf(end);
 %f_PSD=f_PSD.';
 %f_PSD_noise=f_PSD_noise.';
 f_PSD=abs(f_PSD(idxb:idxf));
 f_PSD_noise=abs(f_PSD_noise(idxb:idxf));
 Welch_PSD=abs(Welch_PSD(idxb:idxf));
 Welch_PSD_noise=abs(Welch_PSD_noise(idxb:idxf));
 %Welch_PSD=Welch_PSD-Welch_PSD_noise;
 m0 = trapz(f_PSD,Welch_PSD);
 m1 = trapz(f_PSD,f_PSD.*Welch_PSD); % Calculate first moment
 f_avg=m1/m0;

 Welch_PSD=Welch_PSD-Welch_PSD_noise;
 m0_noise = trapz(f_PSD,Welch_PSD);
 m1_noise = trapz(f_PSD,f_PSD.*Welch_PSD); % Calculate first moment
 f_Noise_avg=m1/m0;


 salida=[f_avg,m1,m0, f_Noise_avg, m1_noise, m0_noise];
end