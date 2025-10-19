import axios from '../interceptor';
import {
    TextBlockCreateReq,
    TextBlockDetail,
    TextBlockPagination,
    TextBlockRes,
    TextBlockUpdateReq,
    GetTextBlockListParam
} from "../../types/textBlockType";

// 获取所有知识库
export function queryTextBlockAll(): Promise<TextBlockPagination> {
    return axios.get('/api/v1/sapper/text_block/all');
}

// 获取知识库详情
export function queryTextBlockDetail(uuid: string): Promise<TextBlockDetail> {
    return axios.get(`/api/v1/sapper/text_block/${uuid}`);
}

// 获取知识库列表（分页）
export function queryTextBlockList(params?: GetTextBlockListParam): Promise<TextBlockPagination> {
    return axios.get('/api/v1/sapper/text_block', {
        params
    });
}

// 创建知识库
export function createTextBlockAPI(data: TextBlockCreateReq): Promise<TextBlockRes> {
    return axios.post(`/api/v1/sapper/text_block`, data);
}

// 更新知识库
export function updateTextBlockAPI(uuid: string, data: TextBlockUpdateReq) {
    return axios.put(`/api/v1/sapper/text_block/${uuid}`, data);
}

// 删除知识库
export function deleteTextBlockAPI(pk: string) {
    return axios.delete(`/api/v1/sapper/text_block/${pk}`);
}
