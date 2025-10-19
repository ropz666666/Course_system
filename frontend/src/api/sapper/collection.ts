import axios from '../interceptor';
import {
    CollectionCreateReq,
    CollectionDetail,
    CollectionPagination,
    CollectionRes,
    CollectionUpdateReq,
    GetCollectionListParam
} from "../../types/collectionType";



// 获取所有知识库
export function queryCollectionAll(): Promise<CollectionPagination> {
    return axios.get('/api/v1/sapper/collection/all');
}

// 获取知识库详情
export function queryCollectionDetail(uuid: string): Promise<CollectionDetail> {
    return axios.get(`/api/v1/sapper/collection/${uuid}`);
}

// 获取知识库列表（分页）
export function queryCollectionList(params?: GetCollectionListParam): Promise<CollectionPagination> {
    return axios.get('/api/v1/sapper/collection', {
        params
    });
}

// 创建知识库
export function createCollectionAPI(data: CollectionCreateReq): Promise<CollectionRes> {
    return axios.post(`/api/v1/sapper/collection`, data);
}

// 更新知识库
export function updateCollectionAPI(uuid: string, data: CollectionUpdateReq) {
    return axios.put(`/api/v1/sapper/collection/${uuid}`, data);
}

// 删除知识库
export function deleteCollectionAPI(pk: string) {
    return axios.delete(`/api/v1/sapper/collection/${pk}`);
}

