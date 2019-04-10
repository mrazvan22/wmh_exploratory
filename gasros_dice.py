import sys
import glob
import os
import configparser
import nipype.algorithms.metrics
import numpy as np
from matplotlib import pyplot as pl
import nibabel as nib


'''gasros_dice.py gasros.cfg '''


config = configparser.ConfigParser()

configFile = sys.argv[1]
config.read(configFile)

outputFolder = config['subject_data']['output_folder'] + '/data/nifti/'

manualSegFolder = '/data/vision/polina/projects/wmh/incoming/2018_05_15/gasros_files/derivatives/'

# glob.iglob('%s/data/nifti/**/*leuk_seg_bin.nii.gz' % output_folder, recursive=True)
subjList = np.array(np.sort([x for x in os.listdir(outputFolder)]))
print(os.listdir(outputFolder))

nrSubj = len(subjList)
# nrSubj = 50

diceList = np.zeros(nrSubj)


for s in range(nrSubj):
  subjName = subjList[s]
  print(subjName)
  segAuto = '%s/%s/images/%s_leuk_seg_bin.nii.gz' % (outputFolder, subjName, subjName)
  segManual = '%s/%s/lesionmask/flair/manual/%s_flair_ax_01_seg_01.nii.gz' % (manualSegFolder, subjName, subjName)
  mriOrig = '%s/%s/images/%s_flair_img_brain.nii.gz' % (outputFolder, subjName, subjName)


  # print('output_folder', outputFolder)
  # print(segAuto)
  # print(segManual)
  overlap = nipype.algorithms.metrics.Overlap()
  overlap.inputs.volume1 = segAuto
  overlap.inputs.volume2 = segManual
  overlap.run()
  diceList[s] = overlap._dice
  print('dice', overlap._dice)

  mriArray = nib.load(mriOrig).get_fdata()
  mriArray /= np.max(mriArray)
  mriSlice = mriArray[:, :, int(mriArray.shape[2] / 2)]
  print(mriArray.shape, type(mriArray))
  segAutoArray = nib.load(segAuto).get_fdata()
  segManualArray = nib.load(segManual).get_fdata()


  opacityMri = 0.6
  mriArray *=  opacityMri

  mriArray[segManualArray == 1] = 1
  mriArray[segAutoArray == 1] = 0.8

  import scipy.misc

  os.system('mkdir -p %s/data/overlay' % config['subject_data']['output_folder'])
  mriOverlay = '%s/data/overlay/%s_flair_overlay.png' % (config['subject_data']['output_folder'], subjName)

  scipy.misc.imsave(mriOverlay, mriArray[:, :, int(mriArray.shape[2] / 2)])
  print(np.max(mriArray))
  print(np.max(segAutoArray))





pl.plot(diceList)

print(subjList[:nrSubj][diceList < 0.4])