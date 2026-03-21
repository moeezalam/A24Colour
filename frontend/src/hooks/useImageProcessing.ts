import { useState, useCallback } from 'react';
import { processImageAsync, getJobStatus } from '../services/api';
import { ProcessingRequest } from '../types';

interface UseImageProcessingReturn {
  processImage: (file: File, request: ProcessingRequest) => Promise<void>;
  isProcessing: boolean;
  progress: number;
  progressMessage: string;
  result: string | null;
  error: string | null;
  reset: () => void;
}

export const useImageProcessing = (): UseImageProcessingReturn => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const pollJobStatus = async (jobId: string) => {
    const pollInterval = 1000; // 1 second
    const maxPolls = 120; // 2 minutes timeout
    let pollCount = 0;

    const poll = async () => {
      try {
        const status = await getJobStatus(jobId);
        
        setProgress(status.progress);
        setProgressMessage(status.message);
        
        if (status.status === 'completed' && status.result) {
          setResult(status.result);
          setIsProcessing(false);
          return;
        }
        
        if (status.status === 'failed') {
          throw new Error(status.message);
        }
        
        if (status.status === 'processing' || status.status === 'queued') {
          pollCount++;
          if (pollCount < maxPolls) {
            setTimeout(poll, pollInterval);
          } else {
            throw new Error('Processing timeout - please try again');
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Processing failed');
        setIsProcessing(false);
      }
    };

    poll();
  };

  const processImage = useCallback(async (file: File, request: ProcessingRequest) => {
    setIsProcessing(true);
    setProgress(0);
    setProgressMessage('Starting AI processing...');
    setError(null);
    setResult(null);

    try {
      const jobResponse = await processImageAsync(file, request);
      await pollJobStatus(jobResponse.job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start processing');
      setIsProcessing(false);
    }
  }, []);

  const reset = useCallback(() => {
    setIsProcessing(false);
    setProgress(0);
    setProgressMessage('');
    setResult(null);
    setError(null);
  }, []);

  return {
    processImage,
    isProcessing,
    progress,
    progressMessage,
    result,
    error,
    reset
  };
};