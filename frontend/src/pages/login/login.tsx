import {useCallback, useState, useEffect, useRef} from "react";
import {Form, Input, Button, Checkbox, Row, Image} from "antd";
import {Link, useLocation} from "react-router-dom";
import {useSelector} from "react-redux";
import {useDispatchUser} from "../../hooks/user";
import './index.css'
import {EyeInvisibleOutlined, EyeOutlined, UserOutlined,LockOutlined,CheckCircleOutlined} from "@ant-design/icons";
import {RootState} from "../../stores";
import {LoginData} from "../../types/userType";

const IPT_RULE_USERNAME = [{required: true, message: "请输入用户名"}];
const IPT_RULE_PASSWORD = [{required: true, message: "请输入密码"}];
const IPT_RULE_CAPTCHA = [{required: true, message: "请输入验证码"}];

function LoginPage() {
    const captchaSrc = useSelector((state: RootState) => state.user.captcha);
	const captchaId = useSelector((state: RootState) => state.user.captcha_id);
    const { status } = useSelector((state: RootState) => state.user);
    const {login, getCaptcha} = useDispatchUser();
    const hasFetchedCaptcha = useRef(false);
    const refreshCaptcha = useCallback(() => {
        getCaptcha();
    }, [getCaptcha]);
    const [passwordVisible, setPasswordVisible] = useState(false);
    const togglePasswordVisibility = () => {
        setPasswordVisible(!passwordVisible);
    };


    useEffect(() => {
        if (!hasFetchedCaptcha.current) {
            refreshCaptcha();
            hasFetchedCaptcha.current = true;
        }
    }, [refreshCaptcha]);

    const location = useLocation();
    const urlParams = new URLSearchParams(location.search);

    const jxnuTokenEncoded = urlParams.get('token');
    const { jxnuLogin } = useDispatchUser();

    useEffect(() => {
        const checkAuth = async () => {
            if (jxnuTokenEncoded) {
                try {
                    const token = decodeURIComponent(jxnuTokenEncoded);
                    await jxnuLogin(`Bearer ${token}`);
                    // 清除URL中的token参数
                    const cleanUrl = window.location.pathname;
                    window.history.replaceState({}, document.title, cleanUrl);
                } catch (error) {
                    console.error('JXNU登录失败:', error);
                }
            }
        };

        checkAuth();
    }, [jxnuTokenEncoded, jxnuLogin]);

    const onFinish = async (values: LoginData) => {
		values.captcha_id = captchaId
        await login(values)
    }

    return (
        <div className="login-container">
            <div className="wrapper">
                <div className="title">智能体创建平台登录</div>
                <Form
                    className="login-form"
                    initialValues={{
                        remember: true,
                    }}
                    onFinish={onFinish}
                >
                    <Form.Item name="username" rules={IPT_RULE_USERNAME}>
                        <Input
                            prefix={<UserOutlined />}
                            placeholder="请输入账号"
                        />
                    </Form.Item>
                    <Form.Item name="password" rules={IPT_RULE_PASSWORD}>
                        <Input
                            type={passwordVisible ? "text" : "password"}
                            autoComplete="off"
                            placeholder="请输入密码"
                            prefix={<LockOutlined />}

                            suffix={
                                passwordVisible ?
                                    <EyeOutlined
                                        onClick={togglePasswordVisibility}
                                        style={{cursor: 'pointer', color: 'inherit'}}
                                    /> :
                                    <EyeInvisibleOutlined
                                        onClick={togglePasswordVisibility}
                                        style={{cursor: 'pointer', color: 'inherit'}}
                                    />
                            }
                        />
                    </Form.Item>
                    <Form.Item name="captcha" rules={IPT_RULE_CAPTCHA}>
                        <Row align="middle">
                            <Input prefix={<CheckCircleOutlined />} placeholder="请输入验证码" style={{width: '60%', flex: 1}}/>
                            <Image
                                src={captchaSrc}
                                preview={false}
                                alt="captcha"
                                onClick={refreshCaptcha}
                                style={{cursor: "pointer", height: "32px", width: "auto"}}
                            />
                        </Row>
                    </Form.Item>
                    <Form.Item>
                        <Form.Item name="remember" valuePropName="checked" noStyle>
                            <Checkbox>记住我</Checkbox>
                        </Form.Item>
                    </Form.Item>
                    <Row justify="space-around">
                        <Button
                            type="primary"
                            htmlType="submit"
                            className="login-form-button"
                            loading={status === 'loading'}
                        >
                            登录
                        </Button>
                        <Link to={"/register"}>
                            <Button>注册</Button>
                        </Link>
                    </Row>
                </Form>
            </div>
        </div>
    );
}

export default LoginPage;
