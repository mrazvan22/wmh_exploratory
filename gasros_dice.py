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

# nrSubj = len(subjList)
nrSubj = 200

diceList = np.zeros(nrSubj)
volAuto = np.zeros(nrSubj)
volManual = np.zeros(nrSubj)

overlayFld = '%s/data/overlay' % config['subject_data']['output_folder']
os.system('mkdir -p %s' % overlayFld)


for s in range(nrSubj):
  subjName = subjList[s]
  print(subjName)
  segAuto = '%s/%s/images/%s_leuk_seg_bin.nii.gz' % (outputFolder, subjName, subjName)
  segManual = '%s/%s/lesionmask/flair/manual/%s_flair_ax_01_seg_01.nii.gz' % (manualSegFolder, subjName, subjName)
  mriOrig = '%s/%s/images/%s_flair_img_brain.nii.gz' % (outputFolder, subjName, subjName)

  overlap = nipype.algorithms.metrics.Overlap()
  overlap.inputs.volume1 = segAuto
  overlap.inputs.volume2 = segManual
  overlap.run()
  diceList[s] = overlap._dice
  print('dice', overlap._dice)

  mriArray = nib.load(mriOrig).get_fdata()
  mriArray /= np.max(mriArray)

  segAutoArray = nib.load(segAuto).get_fdata()
  segManualArray = nib.load(segManual).get_fdata()

  # compute overlays of MRI with binary segmentation of WMHs
  opacityMri = 0.6
  mriArray *=  opacityMri
  mriArrayManual = np.copy(mriArray)
  mriArrayAuto = np.copy(mriArray)

  mriArrayManual[segManualArray == 1] = 1
  mriArrayAuto[segAutoArray == 1] = 1

  # compute volumes of WMH segmentations, for both manual seg. and automatic seg.
  volManual[s] = np.sum(segManualArray)
  volAuto[s] = np.sum(segAutoArray)

  import scipy.misc


  sliceList = range(int(mriArray.shape[2] / 3), 2*int(mriArray.shape[2] / 3))
  # nrSlices = len(sliceList)

  for sliceNrZ in sliceList:
    mriOverlayAuto = '%s/%s_sl%.2d_overlay_auto.png' % (overlayFld, subjName, sliceNrZ)
    mriOverlayManual = '%s/%s_sl%.2d_overlay_manual.png' % (overlayFld, subjName, sliceNrZ)
    mriOverlay = '%s/%s_sl%.2d_overlay_bck.png' % (overlayFld, subjName, sliceNrZ)
    mriOverlayTxt = '%s/%s_sl%.2d_overlay.png' % (overlayFld, subjName, sliceNrZ)

    # scipy.misc.imsave(mriOverlayAuto, mriArrayAuto[:, :, sliceNrZ])
    # scipy.misc.imsave(mriOverlayManual, mriArrayManual[:, :, sliceNrZ])


    sideBySideImages = np.concatenate((mriArrayManual[:, :, sliceNrZ], mriArrayAuto[:, :, sliceNrZ]), axis=1)
    # print(sideBySideImages.shape)
    # print(mriArrayManual[:, :, sliceNrZ].shape)
    scipy.misc.imsave(mriOverlay, sideBySideImages)
    os.system("convert -pointsize 20 -fill white -draw 'text 120,20 \"Manual                  Automatic\" ' %s %s"
              % (mriOverlay, mriOverlayTxt))
    os.system('rm %s' % mriOverlay)


fig1 = pl.figure(1)
pl.hist(diceList)
pl.xlabel('dice score')
fig1.savefig('%s/dice.png' % overlayFld)

print(subjList[:nrSubj][diceList < 0.4])


fig2 = pl.figure(2)

# scatter plot manual against automatic volumes
pl.scatter(volManual, volAuto)

ax = pl.gca()
xLim = ax.get_xlim()
pl.plot(xLim, xLim)
pl.xlabel("manual")
pl.ylabel("automatic")
fig2.savefig('%s/scatter_seg.png' % overlayFld)

pl.show()