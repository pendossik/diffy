import { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

type UserData = {
    email: string;
};

export const useCurrentUser = () => {
    const [user, setUser] = useState<UserData | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUser = async () => {
            const token = localStorage.getItem("access_token");
            if (!token) return;

            try {
                const response = await axios.get(
                    `${import.meta.env.VITE_API_URL}/accounts/current_user/`,
                    {
                        headers: { Authorization: `Bearer ${token}` },
                    },
                );
                setUser(response.data);
            } catch (error: any) {
                console.error("Auth error:", error.response?.data);
                if (error.response?.status === 401) {
                    logout();
                }
            }
        };
        fetchUser();
    }, []);

    const logout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        setUser(null);
        navigate("/");
    };

    return { user, logout };
};
