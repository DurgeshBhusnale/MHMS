import React, { useEffect, useState } from 'react';
import Sidebar from '../../components/Sidebar';
import { apiService } from '../../services/api';

interface DefaultOption {
    option_id: number;
    question_type: 'happy_state' | 'sad_state';
    option_text: string;
    option_text_hindi: string;
    display_order: number;
    is_active: boolean;
    created_at: string;
}

interface OptionsData {
    happy_state_options: DefaultOption[];
    sad_state_options: DefaultOption[];
}

const ManageDefaultQuestions: React.FC = () => {
    const [optionsData, setOptionsData] = useState<OptionsData>({
        happy_state_options: [],
        sad_state_options: []
    });
    const [loading, setLoading] = useState(true);
    const [newOption, setNewOption] = useState({
        happy_state: '',
        sad_state: ''
    });
    const [isAdding, setIsAdding] = useState({
        happy_state: false,
        sad_state: false
    });
    const [deletingId, setDeletingId] = useState<number | null>(null);

    useEffect(() => {
        fetchOptions();
    }, []);

    const fetchOptions = async () => {
        setLoading(true);
        try {
            const response = await apiService.getDefaultQuestionOptions();
            if (response.data.success) {
                setOptionsData({
                    happy_state_options: response.data.happy_state_options || [],
                    sad_state_options: response.data.sad_state_options || []
                });
            }
        } catch (error) {
            console.error('Error fetching default question options:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAddOption = async (questionType: 'happy_state' | 'sad_state') => {
        const optionText = newOption[questionType].trim();
        if (!optionText) return;

        setIsAdding(prev => ({ ...prev, [questionType]: true }));
        
        try {
            await apiService.createDefaultQuestionOption({
                question_type: questionType,
                option_text: optionText
            });
            
            setNewOption(prev => ({ ...prev, [questionType]: '' }));
            await fetchOptions(); // Refresh the list
        } catch (error) {
            console.error('Error adding option:', error);
            alert('Error adding option. Please try again.');
        } finally {
            setIsAdding(prev => ({ ...prev, [questionType]: false }));
        }
    };

    const handleDeleteOption = async (optionId: number) => {
        setDeletingId(optionId);
        
        try {
            await apiService.deleteDefaultQuestionOption(optionId);
            await fetchOptions(); // Refresh the list
        } catch (error) {
            console.error('Error deleting option:', error);
            alert('Error deleting option. Please try again.');
        } finally {
            setDeletingId(null);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent, questionType: 'happy_state' | 'sad_state') => {
        if (e.key === 'Enter') {
            handleAddOption(questionType);
        }
    };

    const renderSection = (
        title: string, 
        questionType: 'happy_state' | 'sad_state', 
        options: DefaultOption[],
        color: string
    ) => (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className={`flex items-center mb-4 pb-3 border-b-2 ${color}`}>
                <i className={`fas ${questionType === 'happy_state' ? 'fa-smile' : 'fa-frown'} text-2xl ${color.replace('border-', 'text-')} mr-3`}></i>
                <h2 className="text-xl font-bold text-gray-800">{title}</h2>
                <span className="ml-auto bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-sm">
                    {options.length} options
                </span>
            </div>

            {/* Add new option input */}
            <div className="mb-4">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={newOption[questionType]}
                        onChange={(e) => setNewOption(prev => ({ ...prev, [questionType]: e.target.value }))}
                        onKeyPress={(e) => handleKeyPress(e, questionType)}
                        placeholder={`Add new ${questionType === 'happy_state' ? 'happy' : 'sad'} state option...`}
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={isAdding[questionType]}
                    />
                    <button
                        onClick={() => handleAddOption(questionType)}
                        disabled={isAdding[questionType] || !newOption[questionType].trim()}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                            isAdding[questionType] || !newOption[questionType].trim()
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : `${color.replace('border-', 'bg-').replace('border-', 'hover:bg-')} text-white hover:opacity-90`
                        }`}
                    >
                        {isAdding[questionType] ? (
                            <i className="fas fa-spinner fa-spin"></i>
                        ) : (
                            <i className="fas fa-plus"></i>
                        )}
                    </button>
                </div>
            </div>

            {/* Options list */}
            <div className="space-y-2 max-h-96 overflow-y-auto">
                {options.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                        <i className={`fas ${questionType === 'happy_state' ? 'fa-smile' : 'fa-frown'} text-4xl mb-3 opacity-50`}></i>
                        <p>No options added yet</p>
                        <p className="text-sm">Click the + button above to add your first option</p>
                    </div>
                ) : (
                    options.map((option, index) => (
                        <div key={option.option_id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                            <div className="flex items-center flex-1">
                                <span className="text-sm text-gray-500 w-6 mr-3">#{index + 1}</span>
                                <div className="flex-1">
                                    <p className="font-medium text-gray-800">{option.option_text}</p>
                                    <p className="text-sm text-gray-600">{option.option_text_hindi}</p>
                                </div>
                            </div>
                            
                            <button
                                onClick={() => handleDeleteOption(option.option_id)}
                                disabled={deletingId === option.option_id}
                                className="ml-3 px-3 py-1 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                                title="Delete option"
                            >
                                {deletingId === option.option_id ? (
                                    <i className="fas fa-spinner fa-spin"></i>
                                ) : (
                                    <i className="fas fa-trash"></i>
                                )}
                            </button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );

    if (loading) {
        return (
            <div className="flex h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
                <Sidebar />
                <div className="flex-1 flex items-center justify-center">
                    <div className="text-center">
                        <i className="fas fa-spinner fa-spin text-4xl text-blue-600 mb-4"></i>
                        <p className="text-gray-600">Loading default questions...</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="flex h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
            <Sidebar />
            <div className="flex-1 p-6 overflow-y-auto">
                <div className="max-w-7xl mx-auto">
                    {/* Header */}
                    <div className="mb-8">
                        <h1 className="text-3xl font-bold text-gray-800 mb-2">
                            Manage Default Questions
                        </h1>
                        <p className="text-gray-600">
                            Configure options for mental health state questions that appear in every survey
                        </p>
                    </div>

                    {/* Instructions */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                        <div className="flex items-start">
                            <i className="fas fa-info-circle text-blue-600 mt-1 mr-3"></i>
                            <div>
                                <h3 className="font-semibold text-blue-800 mb-1">How it works</h3>
                                <p className="text-blue-700 text-sm">
                                    These questions will appear in every survey after the mental health state question. 
                                    Users can select multiple options for each question. Add, edit, or remove options as needed.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Two sections side by side */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {renderSection(
                            'Happy State Options', 
                            'happy_state', 
                            optionsData.happy_state_options,
                            'border-green-500'
                        )}
                        
                        {renderSection(
                            'Sad State Options', 
                            'sad_state', 
                            optionsData.sad_state_options,
                            'border-red-500'
                        )}
                    </div>

                    {/* Statistics */}
                    <div className="mt-8 bg-white rounded-lg shadow-md p-6">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">Statistics</h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="text-center p-4 bg-green-50 rounded-lg">
                                <i className="fas fa-smile text-2xl text-green-600 mb-2"></i>
                                <p className="text-sm text-gray-600">Happy State Options</p>
                                <p className="text-2xl font-bold text-green-600">{optionsData.happy_state_options.length}</p>
                            </div>
                            <div className="text-center p-4 bg-red-50 rounded-lg">
                                <i className="fas fa-frown text-2xl text-red-600 mb-2"></i>
                                <p className="text-sm text-gray-600">Sad State Options</p>
                                <p className="text-2xl font-bold text-red-600">{optionsData.sad_state_options.length}</p>
                            </div>
                            <div className="text-center p-4 bg-blue-50 rounded-lg">
                                <i className="fas fa-list text-2xl text-blue-600 mb-2"></i>
                                <p className="text-sm text-gray-600">Total Options</p>
                                <p className="text-2xl font-bold text-blue-600">
                                    {optionsData.happy_state_options.length + optionsData.sad_state_options.length}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ManageDefaultQuestions;