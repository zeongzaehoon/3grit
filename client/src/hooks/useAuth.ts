import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';

export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ username, password }: { username: string; password: string }) => {
      const loginResponse = await api.login(username, password);
      const userResponse = await api.getUsers();
      const currentUser = userResponse.users.find((user: { email: string }) => user.email === username);
      
      if (!currentUser) {
        throw new Error('User not found');
      }

      return {
        token: loginResponse.access_token,
        user: {
          name: currentUser.name,
          email: currentUser.email
        }
      };
    },
    onSuccess: (data) => {
      localStorage.setItem('token', data.token);
      localStorage.setItem('userInfo', JSON.stringify(data.user));
      api.setToken(data.token);
      queryClient.invalidateQueries({ queryKey: ['users'] });
    }
  });
}

export function useLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
      api.setToken('');
    },
    onSuccess: () => {
      queryClient.clear();
    }
  });
} 