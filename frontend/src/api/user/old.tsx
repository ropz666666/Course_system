import axios from '../interceptor';
import {
    SysUserAddReq,
    SysUserAvatarReq,
    SysUserInfoReq,
    SysUserNoRelationRes, UserAddAgentsReq,
    UserInfo,
} from "../../types/userType";

// 添加智能体到用户
export function addUserAgentAPI(data: UserAddAgentsReq) {
    return axios.post(`/api/v1/sapper/user/agent`, data);
}

export function getUserInfo(): Promise<UserInfo> {
    return axios.get('/api/v1/sapper/user/me');
}

export function changeUserStatus(pk: number) {
    return axios.put(`/api/v1/sapper/user/${pk}/status`);
}

export function changeUserSuper(pk: number) {
    return axios.put(`/api/v1/sapper/user/${pk}/super`);
}

export function changeUserStaff(pk: number) {
    return axios.put(`/api/v1/sapper/user/${pk}/staff`);
}

export function changeUserMulti(pk: number) {
    return axios.put(`/api/v1/sapper/user/${pk}/multi`);
}

export function updateUserAvatar(username: string, data: SysUserAvatarReq) {
    return axios.put(`/api/v1/sapper/user/${username}/avatar`, data);
}

export function updateUser(username: string, data: SysUserInfoReq) {
    return axios.put(`/api/v1/sapper/user/${username}`, data);
}

export function addUser(data: SysUserAddReq): Promise<SysUserNoRelationRes> {
    return axios.post('/api/v1/sapper/user/add', data);
}
export function deleteUser(username: string) {
    return axios.delete(`/api/v1/sapper/user/${username}`);
}
