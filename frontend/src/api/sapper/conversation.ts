import axios from '../interceptor';
import {
    ConversationCreateReq, ConversationDetail,
    ConversationPagination,
    ConversationRes,
    ConversationUpdateReq, GetAllConversationParam, GetConversationListParam
} from "../../types/conversationType.ts";


// 获取所有会话
export function queryConversationAll(params: GetAllConversationParam): Promise<ConversationRes[]> {
    return axios.get('/api/v1/sapper/conversation/all', {
        params
    });
}

// 获取会话详情
export function queryConversationDetail(uuid: string): Promise<ConversationDetail> {
    return axios.get(`/api/v1/sapper/conversation/${uuid}`);
}

// 获取会话列表（分页）
export function queryConversationList(params?: GetConversationListParam): Promise<ConversationPagination> {
    return axios.get('/api/v1/sapper/conversation', {
        params
    });
}

// 创建会话
export function createConversationAPI(data: ConversationCreateReq): Promise<ConversationRes> {
    return axios.post(`/api/v1/sapper/conversation`, data);
}

// 更新会话
export function updateConversationAPI(uuid: string, data: ConversationUpdateReq) {
    return axios.put(`/api/v1/sapper/conversation/${uuid}`, data);
}

// 删除会话
export function deleteConversationAPI(pk: string) {
    return axios.delete(`/api/v1/sapper/conversation/${pk}`);
}