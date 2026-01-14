import * as FileSystem from 'expo-file-system/legacy';

export const modelDir = `${FileSystem.documentDirectory ?? ''}models/`;

export const ensureModelDir = async () => {
  if (!modelDir) throw new Error("FileSystem.documentDirectory is null");
  const dirInfo = await FileSystem.getInfoAsync(modelDir);
  if (!dirInfo.exists) {
    await FileSystem.makeDirectoryAsync(modelDir, { intermediates: true });
  }
};

export const downloadModel = async (url: string, filename: string, onProgress?: (progress: number) => void) => {
  await ensureModelDir();
  const fileUri = `${modelDir}${filename}`;
  
  const downloadResumable = FileSystem.createDownloadResumable(
    url,
    fileUri,
    {},
    (downloadProgress) => {
      const progress = downloadProgress.totalBytesWritten / downloadProgress.totalBytesExpectedToWrite;
      if (onProgress) onProgress(progress);
    }
  );

  try {
    const { uri } = await downloadResumable.downloadAsync() || {};
    return uri;
  } catch (e) {
    console.error(e);
    return null;
  }
};

export const checkFileExists = async (filename: string) => {
  const uri = `${modelDir}${filename}`;
  const info = await FileSystem.getInfoAsync(uri);
  return info.exists;
};

export const getModelPath = (filename: string) => {
  const uri = `${modelDir}${filename}`;
  // Strip file:// prefix for native modules that require absolute paths
  return uri.replace('file://', '');
};
