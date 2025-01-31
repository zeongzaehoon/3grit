// API Types
export interface ChatPayload {
  question: string;
}

export interface CreateUserBody {
  name: string;
  email: string;
  password: string;
}

export interface UpdateUserBody {
  name?: string;
  password?: string;
}

export interface UserResponse {
  id: string;
  name: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface GetUsersResponse {
  total_count: number;
  page: number;
  users: UserResponse[];
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

// API Client
export class APIClient {
  private baseUrl: string;
  private token: string | null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.token = null;
  }

  setToken(token: string) {
    this.token = token;
  }

  private async fetch(endpoint: string, options: RequestInit = {}) {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      ...options.headers,
    };

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  async login(username: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${this.baseUrl}/users/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async createUser(body: CreateUserBody) {
    return this.fetch('/users', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async updateUser(body: UpdateUserBody) {
    return this.fetch('/users', {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  }

  async getUsers(page = 1, itemsPerPage = 10) {
    return this.fetch(`/users?page=${page}&items_per_page=${itemsPerPage}`);
  }

  async sendChat(question: string) {
    return this.fetch('/chat/run', {
      method: 'POST',
      body: JSON.stringify({ question }),
    });
  }

  async getChatHistory() {
    return this.fetch('/chat/history');
  }
}