import { axiosInstance } from './axios';

export interface WorkflowNode {
    id: string;
    node_type: string;
    config: any;
    position: { x: number; y: number };
}

export interface WorkflowEdge {
    id: string;
    source_node: string;
    target_node: string;
    condition?: string;
}

export interface Workflow {
    id: string;
    name: string;
    description?: string;
    status: string;
    is_active: boolean;
    nodes: WorkflowNode[];
    edges: WorkflowEdge[];
    workflow_type?: string;
}

export const workflowApi = {
    getWorkflow: async (workflowId: string): Promise<Workflow> => {
        const response = await axiosInstance.get(`/workflows/${workflowId}`);
        return response.data;
    },

    getWorkflowByChat: async (chatId: string): Promise<Workflow> => {
        const response = await axiosInstance.get(`/workflows/chat/${chatId}`);
        return response.data;
    },

    listWorkflows: async (): Promise<Workflow[]> => {
        const response = await axiosInstance.get('/workflows/');
        return response.data;
    },

    updateGraph: async (workflowId: string, nodes: any[], edges: any[]) => {
        const response = await axiosInstance.put(`/workflows/${workflowId}/graph`, { nodes, edges });
        return response.data;
    },

    toggleActive: async (workflowId: string): Promise<{ is_active: boolean }> => {
        const response = await axiosInstance.post(`/workflows/${workflowId}/toggle-active`);
        return response.data;
    },

    executeWorkflow: async (workflowId: string): Promise<{ execution_id: string, status: string }> => {
        const response = await axiosInstance.post(`/workflows/${workflowId}/execute`);
        return response.data;
    }
};
