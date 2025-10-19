// AuthCallbackPage.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {Spinner} from "react-bootstrap";
import {useDispatchUser} from "../../hooks/user.ts";


const AuthCallbackPage = () => {
    const navigate = useNavigate();
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    const { jxnuLogin } = useDispatchUser();

    useEffect(() => {
        const handleAuthentication = async () => {
            try {
                const params = new URLSearchParams(window.location.search);
                const encryptedToken = params.get('token');
                const iv = params.get('iv');
                const redirect_url = params.get('redirect_url');
                if(encryptedToken && iv)
                    await jxnuLogin({token: encryptedToken, iv});

                // 4. Clean URL and redirect
                window.history.replaceState({}, '', '/');
                setStatus('success');
                if (redirect_url)
                    navigate(redirect_url, { replace: true });
                else
                    navigate('', { replace: true });

            } catch (error) {
                console.error('认证失败:', error);
                setStatus('error');
                setErrorMessage(
                    error instanceof Error
                        ? error.message
                        : '认证过程中发生未知错误'
                );

                // Redirect to login with error state
                navigate('https://ai.jxselab.com/', {
                    state: {
                        error: true,
                        message: error instanceof Error ? error.message : undefined
                    },
                    replace: true
                });
            }
        };

        handleAuthentication();

    }, [navigate]);

    if (status === 'loading') {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen p-8">
                <Spinner />
                <p className="mt-4 text-lg">正在验证登录状态...</p>
            </div>
        );
    }

    if (status === 'error') {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen p-8">
                <div className="text-red-500 text-lg mb-4">
                    认证失败: {errorMessage}
                </div>
                <button
                    onClick={() => navigate('/login')}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                    返回登录页面
                </button>
            </div>
        );
    }

    return null;
};

export default AuthCallbackPage;