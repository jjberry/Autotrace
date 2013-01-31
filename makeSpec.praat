form Open file
  sentence File_name test.wav
  sentence Output_name test.Spectrogram
endform

Read from file... 'file_name$'
Extract left channel
To Spectrogram... 0.005 5000 0.002 20 Gaussian
Write to text file... 'output_name$'

