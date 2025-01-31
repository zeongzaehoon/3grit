import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';

export function useChatHistory() {
  return useQuery({
    queryKey: ['chatHistory'],
    queryFn: () => api.getChatHistory(),
    retry: false
  });
}

export function useSendChat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (question: string) => api.sendChat(question),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chatHistory'] });
    },
  });
} 