import axios from './interceptor';

export interface CourseTreeNode {
  id: number;
  name: string;
  type: 'grade' | 'subject' | 'course';
  children?: CourseTreeNode[];
  course_count?: number;
}

export interface Course {
  id: number;
  title: string;
  description: string;
  teacher_uuid: string;
  grade_id: number;
  subject_id: number;
  cover_image?: string;
  status: number;
  sort_order: number;
  created_time: string;
  updated_time?: string;
  grade?: {
    id: number;
    name: string;
    code: string;
  };
  subject?: {
    id: number;
    name: string;
    code: string;
  };
}

export interface CourseListParams {
  grade_id?: number;
  subject_id?: number;
  status?: number;
  page?: number;
  limit?: number;
}

export interface CourseListResponse {
  items: Course[];
  total: number;
  page: number;
  limit: number;
}

export interface CourseResource {
  id: number;
  uuid: string;
  title: string;
  resource_type: string;
  course_id: number;
  upload_user_uuid: string;
  description?: string;
  file_name?: string;
  file_path?: string;
  file_size?: number;
  file_type?: string;
  download_count: number;
  status: number;
  sort_order?: number;
  created_time: string;
  updated_time?: string;
}

export interface CourseAgent {
  id: number;
  uuid: string;
  course_id: number;
  agent_uuid: string;
  migrated_by: string;
  title: string;
  description?: string;
  sort_order?: number;
  status: number;
  created_time: string;
  updated_time?: string;
  agent?: {
    uuid: string;
    name: string;
    description?: string;
    cover_image?: string;
    type: string;
    status: number;
  };
  migrator?: {
    uuid: string;
    username: string;
    nickname?: string;
    email?: string;
    phone?: string;
    avatar?: string;
  };
}

export interface UpdateCourseAgentParam {
  title?: string;
  description?: string;
  sort_order?: number;
  status?: number;
}

export interface CourseResourceListParams {
  course_id: number;
  resource_type?: string;
  status?: number;
  page?: number;
  limit?: number;
}

export interface CourseResourceListResponse {
  items: CourseResource[];
  total: number;
  page: number;
  limit: number;
}

export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

export const courseApi = {
  // 获取课程树结构
  getCourseTree: (): Promise<ApiResponse<CourseTreeNode[]>> => {
    return axios.get('/api/v1/courses/tree');
  },

  // 获取课程列表
  getCourseList: (params?: CourseListParams): Promise<ApiResponse<CourseListResponse>> => {
    return axios.get('/api/v1/courses', { params });
  },

  // 获取课程详情
  getCourseDetail: (courseId: number): Promise<ApiResponse<Course>> => {
    return axios.get(`/api/v1/courses/${courseId}`);
  },

  // 获取我的课程
  getMyCourses: (): Promise<ApiResponse<Course[]>> => {
    return axios.get('/api/v1/courses/my');
  },

  // 获取年级列表
  getGradeList: (): Promise<ApiResponse<any[]>> => {
    return axios.get('/api/v1/grades');
  },

  // 获取科目列表
  getSubjectList: (): Promise<ApiResponse<any[]>> => {
    return axios.get('/api/v1/subjects');
  },

  // 创建课程
  createCourse: (data: Partial<Course>): Promise<ApiResponse<Course>> => {
    return axios.post('/api/v1/courses', data);
  },

  // 更新课程
  updateCourse: (courseId: number, data: Partial<Course>): Promise<ApiResponse<Course>> => {
    return axios.put(`/api/v1/courses/${courseId}`, data);
  },

  // 删除课程
  deleteCourse: (courseId: number): Promise<ApiResponse<void>> => {
    return axios.delete(`/api/v1/courses/${courseId}`);
  },

  // 获取课程资源列表
  getCourseResources: (params: CourseResourceListParams): Promise<ApiResponse<CourseResourceListResponse>> => {
    return axios.get('/api/v1/course-resources', { params });
  },

  // 获取课程资源详情
  getCourseResourceDetail: (resourceId: number): Promise<ApiResponse<CourseResource>> => {
    return axios.get(`/api/v1/course-resources/${resourceId}`);
  },

  // 下载课程资源
  downloadCourseResource: async (resourceId: number): Promise<Blob> => {
    // 创建一个新的axios实例，绕过响应拦截器
    const axiosInstance = axios.create({
      baseURL: axios.defaults.baseURL,
      withCredentials: axios.defaults.withCredentials,
    });
    
    // 添加请求拦截器以包含认证token
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    const headers: any = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    
    const response = await axiosInstance.get(`/api/v1/course-resources/${resourceId}/download`, {
      responseType: 'blob',
      headers
    });
    return response.data;
  },

  // 预览课程资源
  previewCourseResource: async (resourceId: number): Promise<Blob> => {
    // 创建一个新的axios实例，绕过响应拦截器
    const axiosInstance = axios.create({
      baseURL: axios.defaults.baseURL,
      withCredentials: axios.defaults.withCredentials,
    });
    
    // 添加请求拦截器以包含认证token
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    const headers: any = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    
    const response = await axiosInstance.get(`/api/v1/course-resources/${resourceId}/preview`, {
      responseType: 'blob',
      headers
    });
    return response.data;
  },

  // 创建课程资源
  createCourseResource: (data: FormData): Promise<ApiResponse<CourseResource>> => {
    return axios.post('/api/v1/course-resources', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // 获取课程智能体列表
  getCourseAgents: (courseId: number, status?: number): Promise<ApiResponse<CourseAgent[]>> => {
    const params: any = {};
    if (status !== undefined) {
      params.status = status;
    }
    return axios.get(`/api/v1/course-agents/course/${courseId}`, { params });
  },

  // 从课程中移除智能体
  removeAgentFromCourse: (courseId: number, agentUuid: string): Promise<ApiResponse<void>> => {
    return axios.delete(`/api/v1/course-agents/${courseId}/${agentUuid}`);
  },

  // 更新课程智能体信息
  updateCourseAgent: (courseId: number, agentUuid: string, data: UpdateCourseAgentParam): Promise<ApiResponse<CourseAgent>> => {
    return axios.put(`/api/v1/course-agents/${courseId}/${agentUuid}`, data);
  },

  // 迁移智能体到课程
  migrateAgentToCourse: (data: {
    agent_uuid: string;
    course_id: number;
    title?: string;
    description?: string;
  }): Promise<ApiResponse<CourseAgent>> => {
    return axios.post('/api/v1/course-agents/migrate', data);
  }
};