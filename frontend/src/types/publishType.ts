import {AgentRes} from "./agentType.ts";

export interface AgentPublishment {
    publish_config: Record<string, unknown>;
}

export interface AgentPublishmentRes extends AgentPublishment {
    id: number;
    uuid: string;
    agent_uuid: string;
    channel_uuid: string;
    published_by: string;
    created_time: string;
    updated_time: string;
}

export interface AgentPublishmentDetail extends AgentPublishmentRes {
     agent: AgentRes;
     channel: Record<string, unknown>;
}

export interface AgentPublishmentPagination {
    items: Array<AgentPublishmentRes>;
    links: Array<string>;
    total: number;
    page: number;
    size: number;
    total_pages: number;
}

export interface GetAgentPublishmentListParam {
    page?: number;
    size?: number;
    name?:string
}

export interface PublishmentItem {
    channel_uuid: string
}

export interface AgentPublishmentCreateReq {
    agent_uuid: string;
    channels: PublishmentItem[];
}

export interface AgentPublishmentUpdateReq {
    publish_config?: Record<string, unknown>;
}


export interface AgentPublishmentState {
    status: 'idle' | 'loading' | 'succeeded' | 'failed';
    error: string | null;
    agentPublishments: AgentPublishmentPagination;
    agentPublishmentDetail: AgentPublishmentDetail | null;
}
