import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  hcpName: '',
  interactionType: 'Meeting',
  topics: '',
  sentiment: 'Neutral',
  chatMessages: [],
};

export const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    updateForm: (state, action) => {
      return { ...state, ...action.payload };
    },
    addChatMessage: (state, action) => {
      state.chatMessages.push(action.payload);
    },
  },
});

export const { updateForm, addChatMessage } = interactionSlice.actions;
export default interactionSlice.reducer;
