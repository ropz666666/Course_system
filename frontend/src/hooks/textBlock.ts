import { useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { useSelector, TypedUseSelectorHook } from 'react-redux';
import {
    fetchAllTextBlocks,
    fetchTextBlockList,
    fetchTextBlockDetail,
    createTextBlock,
    updateTextBlock,
    deleteTextBlock
} from '../service/textBlockService';
import { RootState, AppDispatch } from '../stores';
import {resetTextBlockInfo, setTextBlockInfo, setTextBlockStateInfo} from '../stores/textBlockSlice';
import {TextBlockCreateReq, TextBlockDetail, TextBlockState, TextBlockUpdateReq, GetTextBlockListParam} from "../types/textBlockType";


export function useDispatchTextBlock() {
    const dispatch = useDispatch<AppDispatch>();

    // Get all TextBlocks
    const getAllTextBlocks = useCallback(() => {
        return dispatch(fetchAllTextBlocks());
    }, [dispatch]);

    // Get TextBlock list (pagination)
    const getTextBlockList = useCallback((params?: GetTextBlockListParam) => {
        return dispatch(fetchTextBlockList(params));
    }, [dispatch]);

    // Get TextBlock details
    const getTextBlockDetail = useCallback((textBlockUuid: string) => {
        return dispatch(fetchTextBlockDetail(textBlockUuid));
    }, [dispatch]);

    // Create a new TextBlock
    const addTextBlock = useCallback((textBlockData: TextBlockCreateReq) => {
        return dispatch(createTextBlock(textBlockData));
    }, [dispatch]);

    // Update TextBlock information
    const updateTextBlockInfo = useCallback((textBlockUuid: string, data: TextBlockUpdateReq) => {
        return dispatch(updateTextBlock({ textBlockUuid, data }));
    }, [dispatch]);

    // Delete TextBlocks
    const removeTextBlock = useCallback((pk: string) => {
        return dispatch(deleteTextBlock(pk));
    }, [dispatch]);

    // Set partial TextBlock info (partial update)
    const setTextBlockPartialInfo = useCallback((textBlockInfo: Partial<TextBlockDetail>) => {
        dispatch(setTextBlockInfo(textBlockInfo));
    }, [dispatch]);

    // Reset TextBlock info
    const resetTextBlock = useCallback(() => {
        dispatch(resetTextBlockInfo());
    }, [dispatch]);

    // Reset Compile info
    const setTextBlockStatePartialInfo = useCallback((textBlockStateInfo: Partial<TextBlockState>) => {
        dispatch(setTextBlockStateInfo(textBlockStateInfo));
    }, [dispatch]);

    return {
        getAllTextBlocks,
        getTextBlockList,
        getTextBlockDetail,
        addTextBlock,
        updateTextBlockInfo,
        removeTextBlock,
        setTextBlockPartialInfo,
        resetTextBlock,
        setTextBlockStatePartialInfo
    };
}

// Create a typed useSelector hook
export const useTextBlockSelector: TypedUseSelectorHook<RootState> = useSelector;
