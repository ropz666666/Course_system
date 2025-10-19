export interface Plugin {
    name: string;
    description: string;
    cover_image: string;
    status: number;
}

export interface PluginRes extends Plugin {
    uuid: string;
    user_uuid: string;
    created_time: string;
    updated_time: string;
}

export interface PluginDetail extends PluginRes {
    server_url: string;
    parse_path: [];
    header_info: Record<never, never>;
    return_info: Record<never, never>;
    api_parameter:Array<Record<never, never>> | Record<never, never>;
}

export interface PluginPagination {
    items: PluginRes[];
    links: string[];
    total: number;
    page: number;
    size: number;
    total_pages: number;
}

export interface GetPluginListParam {
    page?: number;
    size?: number;
    name?: string;
}

export interface PluginCreateReq {
    name: string;
    description: string;
    cover_image: string;
    status: number;
    server_url: string;
    header_info: Record<never, never>;
    return_info: Record<never, never>;
    api_parameter: Record<never, never>;
}

export interface PluginUpdateReq {
    name?: string;
    description?: string;
    cover_image?: string;
    status?: number;
    server_url?: string;
    header_info: Record<never, never>;
    return_info: Record<never, never>;
    api_parameter: Record<never, never>;
}


export interface PluginState {
    status: 'idle' | 'loading' | 'succeeded' | 'failed';
    error: string | null;
    plugins: PluginPagination;
    pluginDetail: PluginDetail | null;
}
