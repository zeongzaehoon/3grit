import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CreateUserBody, UpdateUserBody } from '../types';
import { api } from '../api/client';

export function useUsers(page: number) {
  return useQuery({
    queryKey: ['users', page],
    queryFn: () => api.getUsers(page),
    retry: false
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userData: CreateUserBody) => api.createUser(userData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userData: UpdateUserBody) => api.updateUser(userData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
} 