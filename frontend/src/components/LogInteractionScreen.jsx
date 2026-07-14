import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateForm, addChatMessage } from '../store/interactionSlice';

export default function LogInteractionScreen() {
  const dispatch = useDispatch();
  const formData = useSelector((state) => state.interaction);
  const chatMessages = useSelector((state) => state.interaction.chatMessages);
  const [chatInput, setChatInput] = useState('');

  const handleInputChange = (e) => {
    dispatch(updateForm({ [e.target.name]: e.target.value }));
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;
    
    const currentInput = chatInput;
  
    dispatch(addChatMessage({ sender: 'user', text: currentInput }));
    setChatInput('');

    try {
    
      const aiPromptContext = `
        Current Form State: ${JSON.stringify(formData)}
        User Message: ${currentInput}
      `;

      // Call FastAPI backend
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    
        body: JSON.stringify({ message: aiPromptContext }), 
      });

      const data = await response.json();
      
      let aiExtractedData = {};
      let aiMessage = "Interaction processed.";

     
      if (typeof data.response === 'string') {
        try {
          aiExtractedData = JSON.parse(data.response);
          aiMessage = aiExtractedData.message || "Updated successfully based on your input.";
        } catch (e) {
        
          console.warn("Could not parse AI response as JSON", data.response);
          aiMessage = data.response;
        }
      } else {
       
        aiExtractedData = data;
        aiMessage = aiExtractedData.message || "Updated successfully.";
      }

    
      const updatedFields = {};
      
      
      const capitalize = (s) => s ? s.charAt(0).toUpperCase() + s.slice(1).toLowerCase() : s;

      if (aiExtractedData.hcp_name) {
        updatedFields.hcpName = aiExtractedData.hcp_name;
      }
      if (aiExtractedData.interaction_type) {
        updatedFields.interactionType = capitalize(aiExtractedData.interaction_type);
      }
      if (aiExtractedData.discussion_topics) {
        updatedFields.topics = aiExtractedData.discussion_topics;
      }
      if (aiExtractedData.sentiment) {
        updatedFields.sentiment = capitalize(aiExtractedData.sentiment);
      }

      
      if (Object.keys(updatedFields).length > 0) {
        dispatch(updateForm(updatedFields));
      }
      
    
      dispatch(addChatMessage({ sender: 'ai', text: aiMessage }));
      
    } catch (error) {
      console.error("Chat error:", error);
      dispatch(addChatMessage({ sender: 'ai', text: "Sorry, I encountered an error connecting to the server." }));
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 p-6 gap-6">
      
      {/* Structured Form Section */}
      <div className="flex-1 bg-white shadow-sm rounded-lg p-6 overflow-y-auto">
        <h2 className="text-xl font-semibold mb-6">Interaction Details</h2>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">HCP Name</label>
            <input 
              name="hcpName"
              value={formData.hcpName || ''}
              onChange={handleInputChange}
              className="w-full border rounded p-2" 
              placeholder="Search or select HCP..." 
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Interaction Type</label>
            <select 
              name="interactionType"
              value={formData.interactionType || ''}
              onChange={handleInputChange}
              className="w-full border rounded p-2"
            >
              <option value="">Select...</option>
              <option value="Meeting">Meeting</option>
              <option value="Email">Email</option>
              <option value="Call">Call</option>
            </select>
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm text-gray-600 mb-1">Topics Discussed</label>
          <textarea 
            name="topics"
            value={formData.topics || ''}
            onChange={handleInputChange}
            className="w-full border rounded p-2 h-24" 
            placeholder="Enter key discussion points..." 
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm text-gray-600 mb-2">Observed/Inferred HCP Sentiment</label>
          <div className="flex gap-4">
            {['Positive', 'Neutral', 'Negative'].map(sentiment => (
              <label key={sentiment} className="flex items-center gap-1">
                <input 
                  type="radio" 
                  name="sentiment" 
                  value={sentiment}
                  checked={formData.sentiment === sentiment}
                  onChange={handleInputChange}
                />
                {sentiment}
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* AI Chat Interface */}
      <div className="w-96 bg-white shadow-sm rounded-lg p-6 flex flex-col">
        <div className="flex items-center gap-2 mb-4 border-b pb-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
          <h2 className="font-semibold text-gray-700">AI Assistant</h2>
        </div>
        
        <div className="flex-1 overflow-y-auto mb-4 bg-gray-50 p-4 rounded border">
          <p className="text-sm text-gray-500 mb-4">
            Log interaction details here (e.g., "Met Dr. Smith, discussed Product X efficacy...") or ask for help.
          </p>
          {chatMessages?.map((msg, idx) => (
            <div key={idx} className={`mb-3 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
              <span className={`inline-block p-2 rounded-lg text-sm ${msg.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800'}`}>
                {msg.text}
              </span>
            </div>
          ))}
        </div>

        <div className="flex gap-2">
          <input 
            type="text" 
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendChatMessage()}
            className="flex-1 border rounded p-2" 
            placeholder="Describe interaction..." 
          />
          <button 
            onClick={sendChatMessage}
            className="bg-gray-600 text-white px-4 py-2 rounded font-medium"
          >
            Log
          </button>
        </div>
      </div>
      
    </div>
  );
}