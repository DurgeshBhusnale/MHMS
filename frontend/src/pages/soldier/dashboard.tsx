import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { apiService } from '../../services/api';

interface SurveySession {
    session_id: number;
    questionnaire_title: string;
    completion_timestamp: string;
    combined_score: number;
    nlp_score: number;
    image_score: number;
    risk_level: string;
    mental_state_rating?: number;
    total_questions: number;
    completion_time_minutes?: number;
}

interface SoldierStats {
    total_surveys: number;
    average_score: number;
    latest_risk_level: string;
    days_since_last_survey: number;
    improvement_trend: 'improving' | 'stable' | 'concerning' | 'unknown';
}

const SoldierDashboard: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    
    // Get soldier data from navigation state
    const soldierData = location.state as { 
        force_id: string; 
        password: string; 
        authenticated?: boolean;
        auth_timestamp?: number;
    } | null;

    const [surveyHistory, setSurveyHistory] = useState<SurveySession[]>([]);
    const [soldierStats, setSoldierStats] = useState<SoldierStats | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [showError, setShowError] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [activeQuestionnaire, setActiveQuestionnaire] = useState<any>(null);

    // Check authentication and redirect if needed
    useEffect(() => {
        if (!soldierData) {
            console.log('No soldier data - redirecting to login');
            navigate('/soldier/login');
            return;
        }

        if (!soldierData.authenticated) {
            console.log('Soldier not authenticated - redirecting');
            navigate('/soldier/login');
            return;
        }

        // Check authentication timestamp (10 minutes max age)
        if (soldierData.auth_timestamp) {
            const authAge = Date.now() - soldierData.auth_timestamp;
            const maxAuthAge = 10 * 60 * 1000; // 10 minutes
            
            if (authAge > maxAuthAge) {
                console.log('Authentication expired - redirecting to login');
                navigate('/soldier/login');
                return;
            }
        }

        console.log('Soldier authentication verified for dashboard');
        loadDashboardData();
    }, [soldierData, navigate]);

    const loadDashboardData = async () => {
        if (!soldierData?.force_id) return;

        try {
            setIsLoading(true);
            
            // Load survey history
            console.log('Loading survey history for:', soldierData.force_id);
            const historyResponse = await apiService.getUserSurveyHistory(soldierData.force_id);
            
            if (historyResponse.data.success) {
                const sessions = historyResponse.data.sessions || [];
                setSurveyHistory(sessions);
                
                // Calculate soldier stats
                if (sessions.length > 0) {
                    const stats = calculateSoldierStats(sessions);
                    setSoldierStats(stats);
                }
            }

            // Load active questionnaire info
            try {
                const questionnaireResponse = await apiService.getActiveQuestionnaire();
                if (questionnaireResponse.data.questionnaire) {
                    setActiveQuestionnaire(questionnaireResponse.data.questionnaire);
                }
            } catch (error) {
                console.warn('Could not load active questionnaire:', error);
            }

        } catch (error: any) {
            console.error('Error loading dashboard data:', error);
            setErrorMessage('Failed to load dashboard data. Please try again.');
            setShowError(true);
        } finally {
            setIsLoading(false);
        }
    };

    const calculateSoldierStats = (sessions: SurveySession[]): SoldierStats => {
        const totalSurveys = sessions.length;
        const averageScore = sessions.reduce((sum, session) => sum + (session.combined_score || 0), 0) / totalSurveys;
        const latestSession = sessions[0]; // Assuming sorted by date desc
        const latestRiskLevel = latestSession?.risk_level || 'UNKNOWN';
        
        // Calculate days since last survey
        const daysSinceLastSurvey = latestSession 
            ? Math.floor((Date.now() - new Date(latestSession.completion_timestamp).getTime()) / (1000 * 60 * 60 * 24))
            : 999;

        // Calculate improvement trend (last 3 surveys)
        let improvementTrend: 'improving' | 'stable' | 'concerning' | 'unknown' = 'unknown';
        if (sessions.length >= 3) {
            const recent3 = sessions.slice(0, 3).reverse(); // Get last 3, oldest first
            const firstScore = recent3[0].combined_score || 0;
            const lastScore = recent3[2].combined_score || 0;
            const difference = lastScore - firstScore;
            
            if (difference <= -0.1) {
                improvementTrend = 'improving'; // Score decreased (better mental health)
            } else if (difference >= 0.1) {
                improvementTrend = 'concerning'; // Score increased (worse mental health)
            } else {
                improvementTrend = 'stable';
            }
        }

        return {
            total_surveys: totalSurveys,
            average_score: averageScore,
            latest_risk_level: latestRiskLevel,
            days_since_last_survey: daysSinceLastSurvey,
            improvement_trend: improvementTrend
        };
    };

    const getRiskLevelColor = (riskLevel: string) => {
        switch (riskLevel?.toUpperCase()) {
            case 'LOW': return 'text-green-600 bg-green-50 border-green-200';
            case 'MEDIUM': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
            case 'HIGH': return 'text-orange-600 bg-orange-50 border-orange-200';
            case 'CRITICAL': return 'text-red-600 bg-red-50 border-red-200';
            default: return 'text-gray-600 bg-gray-50 border-gray-200';
        }
    };

    const getTrendIcon = (trend: string) => {
        switch (trend) {
            case 'improving': return { icon: 'fa-arrow-up', color: 'text-green-600', text: 'Improving' };
            case 'concerning': return { icon: 'fa-arrow-down', color: 'text-red-600', text: 'Needs Attention' };
            case 'stable': return { icon: 'fa-minus', color: 'text-blue-600', text: 'Stable' };
            default: return { icon: 'fa-question', color: 'text-gray-600', text: 'Unknown' };
        }
    };

    const handleStartSurvey = () => {
        if (!activeQuestionnaire) {
            setErrorMessage('No active survey available at this time.');
            setShowError(true);
            return;
        }

        // Navigate to survey with soldier data
        navigate('/soldier/survey', {
            state: {
                force_id: soldierData?.force_id,
                password: soldierData?.password,
                authenticated: true,
                auth_timestamp: soldierData?.auth_timestamp || Date.now()
            }
        });
    };

    const handleLogout = () => {
        navigate('/soldier/login', { replace: true });
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-IN', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full mb-4 shadow-xl">
                        <i className="fas fa-chart-line text-white text-2xl animate-pulse"></i>
                    </div>
                    <div className="text-xl font-semibold text-gray-700 mb-2">Loading Dashboard...</div>
                    <div className="flex justify-center space-x-1">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-100"></div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-200"></div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 relative overflow-hidden">
            {/* Background Elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-20 right-20 w-32 h-32 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full opacity-10 animate-pulse"></div>
                <div className="absolute bottom-40 left-20 w-24 h-24 bg-gradient-to-r from-green-400 to-blue-400 rounded-full opacity-10 animate-bounce"></div>
            </div>

            <div className="relative z-10 container mx-auto px-4 py-6">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div className="flex items-center">
                        <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full mr-4 shadow-lg flex items-center justify-center">
                            <i className="fas fa-user text-white text-xl"></i>
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                                Soldier Dashboard
                            </h1>
                            <p className="text-gray-600">Force ID: {soldierData?.force_id}</p>
                        </div>
                    </div>
                    
                    <button
                        onClick={handleLogout}
                        className="bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 text-white font-semibold py-2 px-4 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200"
                    >
                        <i className="fas fa-sign-out-alt mr-2"></i>
                        Logout
                    </button>
                </div>

                {/* Stats Cards */}
                {soldierStats && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        {/* Total Surveys */}
                        <div className="bg-white/80 backdrop-blur-xl rounded-xl shadow-lg border border-white/20 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Total Surveys</p>
                                    <p className="text-2xl font-bold text-blue-600">{soldierStats.total_surveys}</p>
                                </div>
                                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                                    <i className="fas fa-clipboard-list text-blue-600 text-xl"></i>
                                </div>
                            </div>
                        </div>

                        {/* Latest Risk Level */}
                        <div className="bg-white/80 backdrop-blur-xl rounded-xl shadow-lg border border-white/20 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Current Status</p>
                                    <p className={`text-lg font-bold px-2 py-1 rounded-md border ${getRiskLevelColor(soldierStats.latest_risk_level)}`}>
                                        {soldierStats.latest_risk_level}
                                    </p>
                                </div>
                                <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                                    <i className="fas fa-heartbeat text-gray-600 text-xl"></i>
                                </div>
                            </div>
                        </div>

                        {/* Trend */}
                        <div className="bg-white/80 backdrop-blur-xl rounded-xl shadow-lg border border-white/20 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Trend</p>
                                    <div className="flex items-center">
                                        <i className={`fas ${getTrendIcon(soldierStats.improvement_trend).icon} ${getTrendIcon(soldierStats.improvement_trend).color} mr-2`}></i>
                                        <p className={`text-lg font-bold ${getTrendIcon(soldierStats.improvement_trend).color}`}>
                                            {getTrendIcon(soldierStats.improvement_trend).text}
                                        </p>
                                    </div>
                                </div>
                                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                                    <i className="fas fa-chart-line text-green-600 text-xl"></i>
                                </div>
                            </div>
                        </div>

                        {/* Days Since Last Survey */}
                        <div className="bg-white/80 backdrop-blur-xl rounded-xl shadow-lg border border-white/20 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Last Survey</p>
                                    <p className="text-2xl font-bold text-purple-600">
                                        {soldierStats.days_since_last_survey === 0 ? 'Today' : `${soldierStats.days_since_last_survey}d ago`}
                                    </p>
                                </div>
                                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                                    <i className="fas fa-clock text-purple-600 text-xl"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Action Section */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Start Survey Card */}
                    <div className="lg:col-span-1">
                        <div className="bg-white/80 backdrop-blur-xl rounded-xl shadow-lg border border-white/20 p-6">
                            <div className="text-center">
                                <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full mx-auto mb-4 flex items-center justify-center shadow-lg">
                                    <i className="fas fa-play text-white text-2xl"></i>
                                </div>
                                <h3 className="text-xl font-bold text-gray-800 mb-2">Mental Health Survey</h3>
                                <p className="text-gray-600 mb-6">
                                    Take your regular mental health assessment to help us monitor your well-being.
                                </p>
                                
                                {activeQuestionnaire && (
                                    <div className="bg-blue-50 rounded-lg p-3 mb-4 border border-blue-200">
                                        <p className="text-sm font-medium text-blue-800">{activeQuestionnaire.title}</p>
                                        <p className="text-xs text-blue-600">{activeQuestionnaire.description}</p>
                                    </div>
                                )}
                                
                                <button
                                    onClick={handleStartSurvey}
                                    disabled={!activeQuestionnaire}
                                    className={`w-full font-semibold py-3 px-6 rounded-lg shadow-lg transition-all duration-200 ${
                                        activeQuestionnaire
                                            ? 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white hover:scale-105'
                                            : 'bg-gray-400 text-gray-200 cursor-not-allowed'
                                    }`}
                                >
                                    <i className="fas fa-clipboard-list mr-2"></i>
                                    {activeQuestionnaire ? 'Start Survey' : 'No Survey Available'}
                                </button>

                                {/* AI Assistant Entry */}
                                <div className="mt-4">
                                    <button
                                        onClick={() => navigate('/chat')}
                                        className="w-full font-semibold py-3 px-6 rounded-lg shadow-lg transition-all duration-200 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white hover:scale-105 flex items-center justify-center"
                                    >
                                        <i className="fas fa-robot mr-2"></i>
                                        Talk to AI Assistant
                                    </button>
                                    <p className="text-xs text-gray-500 mt-2">Private, on-device AI support. Requires login.</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Survey History */}
                    <div className="lg:col-span-2">
                        <div className="bg-white/80 backdrop-blur-xl rounded-xl shadow-lg border border-white/20 p-6">
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-xl font-bold text-gray-800">Recent Survey History</h3>
                                <i className="fas fa-history text-gray-400"></i>
                            </div>
                            
                            {surveyHistory.length > 0 ? (
                                <div className="space-y-4 max-h-96 overflow-y-auto">
                                    {surveyHistory.slice(0, 5).map((session, index) => (
                                        <div key={session.session_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200">
                                            <div className="flex items-center justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center mb-2">
                                                        <h4 className="font-semibold text-gray-800 mr-3">{session.questionnaire_title}</h4>
                                                        <span className={`text-xs px-2 py-1 rounded-full border ${getRiskLevelColor(session.risk_level)}`}>
                                                            {session.risk_level}
                                                        </span>
                                                    </div>
                                                    <p className="text-sm text-gray-600 mb-1">
                                                        Completed: {formatDate(session.completion_timestamp)}
                                                    </p>
                                                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                                                        <span>Questions: {session.total_questions}</span>
                                                        {session.completion_time_minutes && (
                                                            <span>Duration: {session.completion_time_minutes}min</span>
                                                        )}
                                                        {session.mental_state_rating && (
                                                            <span>Mental State: {session.mental_state_rating}/7</span>
                                                        )}
                                                    </div>
                                                </div>
                                                <div className="text-right ml-4">
                                                    <div className="text-lg font-bold text-blue-600">
                                                        {(session.combined_score * 100).toFixed(0)}%
                                                    </div>
                                                    <div className="text-xs text-gray-500">Combined Score</div>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                    
                                    {surveyHistory.length > 5 && (
                                        <div className="text-center pt-4">
                                            <p className="text-sm text-gray-500">
                                                Showing latest 5 surveys of {surveyHistory.length} total
                                            </p>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="text-center py-8">
                                    <i className="fas fa-clipboard text-gray-300 text-4xl mb-4"></i>
                                    <p className="text-gray-500">No survey history available</p>
                                    <p className="text-sm text-gray-400">Complete your first survey to see history here</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Error Modal */}
            {showError && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl p-6 max-w-md mx-4 shadow-2xl">
                        <div className="text-center">
                            <div className="w-12 h-12 bg-red-100 rounded-full mx-auto mb-4 flex items-center justify-center">
                                <i className="fas fa-exclamation-triangle text-red-600 text-xl"></i>
                            </div>
                            <h3 className="text-lg font-bold text-gray-800 mb-2">Error</h3>
                            <p className="text-gray-600 mb-6">{errorMessage}</p>
                            <button
                                onClick={() => setShowError(false)}
                                className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-lg transition-all duration-200"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SoldierDashboard;