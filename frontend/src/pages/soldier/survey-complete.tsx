import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface LocationState {
    force_id?: string;
    completed_at?: string;
}

const SurveyComplete: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [showAnimation, setShowAnimation] = useState(false);
    
    const state = location.state as LocationState;
    const forceId = state?.force_id;
    const completedAt = state?.completed_at;

    useEffect(() => {
        // Trigger animation after component mounts
        const timer = setTimeout(() => {
            setShowAnimation(true);
        }, 100);

        return () => clearTimeout(timer);
    }, []);

    const handleReturnToLogin = () => {
        navigate('/soldier/login', { replace: true });
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 relative overflow-hidden flex items-center justify-center">
            {/* Background Decorative Elements */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute -top-4 -right-4 w-24 h-24 bg-green-200 rounded-full opacity-60 animate-pulse"></div>
                <div className="absolute top-1/4 -left-8 w-32 h-32 bg-emerald-200 rounded-full opacity-40 animate-bounce"></div>
                <div className="absolute bottom-1/4 right-1/4 w-16 h-16 bg-teal-200 rounded-full opacity-50 animate-pulse delay-1000"></div>
                <div className="absolute bottom-8 left-8 w-20 h-20 bg-green-100 rounded-full opacity-70 animate-bounce delay-500"></div>
            </div>

            {/* Main Content */}
            <div className="w-full max-w-2xl mx-auto p-6 relative z-10">
                <div className={`bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-8 text-center transform transition-all duration-1000 ${
                    showAnimation ? 'scale-100 opacity-100 translate-y-0' : 'scale-95 opacity-0 translate-y-4'
                }`}>
                    {/* Success Icon */}
                    <div className="mx-auto flex items-center justify-center h-24 w-24 rounded-full bg-gradient-to-r from-green-400 to-emerald-500 mb-6 shadow-xl transform animate-pulse">
                        <div className="flex items-center justify-center h-20 w-20 rounded-full bg-white">
                            <i className="fas fa-check text-4xl text-green-500"></i>
                        </div>
                    </div>

                    {/* Success Message */}
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-4">
                        Survey Completed Successfully!
                    </h1>

                    <p className="text-xl text-gray-700 mb-2 font-medium">
                        Thank you for completing the mental health assessment
                    </p>

                    <p className="text-gray-600 mb-8 leading-relaxed">
                        Your responses have been recorded and will help us better understand and support your mental well-being. 
                        Your participation contributes to the overall health and welfare program.
                    </p>

                    {/* Completion Details */}
                    {(forceId || completedAt) && (
                        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 mb-8 border border-green-200">
                            <h3 className="text-lg font-semibold text-green-800 mb-3">Survey Details</h3>
                            <div className="space-y-2 text-sm">
                                {forceId && (
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-600">Force ID:</span>
                                        <span className="font-mono font-semibold text-green-700">{forceId}</span>
                                    </div>
                                )}
                                {completedAt && (
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-600">Completed At:</span>
                                        <span className="font-semibold text-green-700">
                                            {new Date(completedAt).toLocaleString('en-IN', {
                                                day: '2-digit',
                                                month: 'short',
                                                year: 'numeric',
                                                hour: '2-digit',
                                                minute: '2-digit',
                                                hour12: true
                                            })}
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Decorative Elements */}
                    <div className="flex justify-center space-x-2 mb-8">
                        <div className="w-3 h-3 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full animate-bounce"></div>
                        <div className="w-3 h-3 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full animate-bounce delay-100"></div>
                        <div className="w-3 h-3 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full animate-bounce delay-200"></div>
                    </div>

                    {/* Action Buttons */}
                    <div className="space-y-4">
                        <button
                            onClick={handleReturnToLogin}
                            className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-semibold py-4 px-8 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all duration-200 flex items-center justify-center"
                        >
                            <i className="fas fa-home mr-3"></i>
                            Return to Login
                        </button>
                        
                        <p className="text-sm text-gray-500">
                            You will be redirected to the login page to start a new session
                        </p>
                    </div>

                    {/* Footer Message */}
                    <div className="mt-8 pt-6 border-t border-gray-200">
                        <div className="flex items-center justify-center text-gray-500 text-sm">
                            <i className="fas fa-shield-alt mr-2"></i>
                            <span>Your data is secure and confidential</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Floating Elements Animation */}
            <div className="absolute top-16 left-1/4 w-4 h-4 bg-green-300 rounded-full opacity-60 animate-ping"></div>
            <div className="absolute bottom-32 right-1/3 w-6 h-6 bg-emerald-300 rounded-full opacity-40 animate-ping delay-1000"></div>
            <div className="absolute top-1/3 right-16 w-5 h-5 bg-teal-300 rounded-full opacity-50 animate-ping delay-2000"></div>
        </div>
    );
};

export default SurveyComplete;