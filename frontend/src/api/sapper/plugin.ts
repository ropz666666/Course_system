import axios from '../interceptor';
import {
    PluginCreateReq,
    PluginDetail,
    PluginPagination,
    PluginRes,
    PluginUpdateReq,
    GetPluginListParam
} from "../../types/pluginType";



// 获取所有智能体
export function queryPluginAll(): Promise<PluginDetail[]> {
    return axios.get('/api/v1/sapper/plugin/all');
}

// 获取智能体详情
export function queryPluginDetail(uuid: string): Promise<PluginDetail> {
    return axios.get(`/api/v1/sapper/plugin/${uuid}`);
}

// 获取智能体列表（分页）
export function queryPluginList(params?: GetPluginListParam): Promise<PluginPagination> {
    return axios.get('/api/v1/sapper/plugin', {
        params
    });
}

// 创建智能体
export function createPluginAPI(data: PluginCreateReq): Promise<PluginRes> {
    return axios.post(`/api/v1/sapper/plugin`, data);
}

// 更新智能体
export function updatePluginAPI(uuid: string, data: PluginUpdateReq) {
    return axios.put(`/api/v1/sapper/plugin/${uuid}`, data);
}

// 删除智能体
export function deletePluginAPI(pk: string) {
    return axios.delete(`/api/v1/sapper/plugin/${pk}`);
}

