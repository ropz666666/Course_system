import axios from '../interceptor';
// import qs from 'query-string';
import {
    AgentCreateReq,
    AgentDetail,
    AgentPagination,
    AgentRes,
    AgentResetKnowledgeBasesReq,
    AgentResetPluginsReq,
    AgentUpdateReq,
    GetAgentListParam
} from "../../types/agentType";
import {getToken} from "../../utils/auth";
import {GenerateAnswerParam} from "../../types/conversationType.ts";


// 获取所有智能体
export function queryAgentAll(): Promise<AgentPagination> {
    return axios.get('/api/v1/sapper/agent/all');
}

// 获取所有智能体
export function queryPublicAgentList(params?: GetAgentListParam): Promise<AgentPagination> {
    return axios.get('/api/v1/sapper/agent/all/public', {
        params
    });
}

// 获取智能体详情
export function queryAgentDetail(uuid: string): Promise<AgentDetail> {
    return axios.get(`/api/v1/sapper/agent/${uuid}`);
}

// 获取智能体列表（分页）
export function queryAgentList(params?: GetAgentListParam): Promise<AgentPagination> {
    return axios.get('/api/v1/sapper/agent', {
        params
    });
}

// 创建智能体
export function createAgentAPI(data: AgentCreateReq): Promise<AgentRes> {
    return axios.post(`/api/v1/sapper/agent`, data);
}

// 更新智能体
export function updateAgentAPI(uuid: string, data: AgentUpdateReq) {
    return axios.put(`/api/v1/sapper/agent/${uuid}`, data);
}

// 添加插件到智能体
export function resetAgentPluginAPI(uuid: string, data: AgentResetPluginsReq) {
    return axios.post(`/api/v1/sapper/agent/${uuid}/plugin`, data);
}

// 添加知识库到智能体
export function resetAgentKnowledgeBaseAPI(uuid: string, data: AgentResetKnowledgeBasesReq) {
    return axios.post(`/api/v1/sapper/agent/${uuid}/knowledge_base`, data);
}

// 收藏该智能体
export function setAgentFavoriteAPI(uuid: string, favorite: boolean) {
    return axios.put(`/api/v1/sapper/agent/${uuid}/favorite`, {favorite});
}

// 收藏该智能体
export function setAgentRatingAPI(uuid: string, rating_value: number) {
    return axios.put(`/api/v1/sapper/agent/${uuid}/rating`, {rating_value});
}

// 删除智能体
export function deleteAgentAPI(pk: string) {
    return axios.delete(`/api/v1/sapper/agent/${pk}`);
}

export function generateSplFormStream(uuid: string) {
    try {
        // 使用 fetch 请求来处理流式响应
        return fetch(`${import.meta.env.VITE_API_BASE_URL}api/v1/sapper/agent/generate_spl_form/${uuid}`, {
            headers: {
                Authorization: `Bearer ${getToken()}`,  // 认证 token
            }
        });
    } catch (error) {
        console.error('Error while streaming data:', error);
    }
}

export function generateAnswerStream(uuid: string, message: GenerateAnswerParam, controller: AbortController) {
    try {
        return fetch(`${import.meta.env.VITE_API_BASE_URL}api/v1/sapper/agent/generate_answer/${uuid}`, {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${getToken()}`,
            },
            body: JSON.stringify(message),
            signal: controller.signal
        });
    } catch (error) {
        controller.abort();
        throw error;
    }
}


export function generateDebugAnswerStream(uuid: string, debug_unit: number, message: GenerateAnswerParam) {
    try {
        // 使用 fetch 请求来处理流式响应
        const new_message = {...message}
        new_message["debug_unit"] = debug_unit
        return fetch(`${import.meta.env.VITE_API_BASE_URL}api/v1/sapper/agent/generate_debug/${uuid}`, {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${getToken()}`,  // 认证 token
            },
            body: JSON.stringify(new_message)
        });
    } catch (error) {
        console.error('Error while streaming data:', error);
    }
}

export function generateSplChainStream(uuid: string) {
    try {
        // 使用 fetch 请求来处理流式响应
        return fetch(`${import.meta.env.VITE_API_BASE_URL}api/v1/sapper/agent/generate_spl_chain/${uuid}`, {
            headers: {
                Authorization: `Bearer ${getToken()}`,  // 认证 token
            }
        });
    } catch (error) {
        console.error('Error while streaming data:', error);
    }
}

// 下载智能体：返回 Response 对象
export async function downloadAgentAPI(uuid: string): Promise<Response> {
    return fetch(`${import.meta.env.VITE_API_BASE_URL}api/v1/sapper/agent/download/${uuid}`, {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${getToken()}`,
        }
    });
}

