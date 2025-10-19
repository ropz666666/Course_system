import axios from '../interceptor';
import {
    AgentPublishmentCreateReq,
    AgentPublishmentDetail,
    AgentPublishmentPagination,
    AgentPublishmentRes,
    AgentPublishmentUpdateReq,
    GetAgentPublishmentListParam
} from "../../types/publishType";


// 获取所有发布情况
export function queryAgentPublishmentAll(): Promise<AgentPublishmentPagination> {
    return axios.get('/api/v1/sapper/publish/all');
}

// 获取发布情况详情
export function queryAgentPublishmentDetail(uuid: string): Promise<AgentPublishmentDetail> {
    return axios.get(`/api/v1/sapper/publish/${uuid}`);
}

// 获取发布情况列表（分页）
export function queryAgentPublishmentList(params?: GetAgentPublishmentListParam): Promise<AgentPublishmentPagination> {
    return axios.get('/api/v1/sapper/publish', {
        params
    });
}

// 创建发布情况
export function createAgentPublishmentAPI(data: AgentPublishmentCreateReq): Promise<AgentPublishmentRes> {
    return axios.post(`/api/v1/sapper/publish`, data);
}

// 更新发布情况
export function updateAgentPublishmentAPI(uuid: string, data: AgentPublishmentUpdateReq) {
    return axios.put(`/api/v1/sapper/publish/${uuid}`, data);
}

// 删除发布情况
export function deleteAgentPublishmentAPI(pk: string) {
    return axios.delete(`/api/v1/sapper/publish/${pk}`);
}

