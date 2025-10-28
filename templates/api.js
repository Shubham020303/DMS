// Generic API handler
const handleAPIRequest = async (url, method = 'GET', data = null) => {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        const responseData = await response.json();

        if (responseData.status !== 'success') {
            throw new Error(responseData.message || 'API request failed');
        }

        return responseData;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};

// Payment APIs
const paymentAPI = {
    getPayments: () => handleAPIRequest('/getPaymentData/'),
    addPayment: (data) => handleAPIRequest('/manage-payment/', 'POST', data),
    updatePayment: (id, data) => handleAPIRequest(`/manage-payment/${id}/`, 'PUT', data),
    deletePayment: (id) => handleAPIRequest(`/manage-payment/${id}/`, 'DELETE'),
};

// Student Leave APIs
const leaveAPI = {
    getLeaves: () => handleAPIRequest('/getStudentOnLeaveData/'),
    addLeave: (data) => handleAPIRequest('/manage-leave/', 'POST', data),
    updateLeave: (id, data) => handleAPIRequest(`/manage-leave/${id}/`, 'PUT', data),
    deleteLeave: (id) => handleAPIRequest(`/manage-leave/${id}/`, 'DELETE'),
};

// Notification APIs
const notificationAPI = {
    getNotifications: () => handleAPIRequest('/getNotificationData/'),
    markAsRead: (id) => handleAPIRequest(`/manage-Notification/${id}/`, 'PUT'),
    deleteNotification: (id) => handleAPIRequest(`/manage-Notification/${id}/`, 'DELETE'),
};

// Earnings APIs
const earningsAPI = {
    getEarnings: () => handleAPIRequest('/getEearningData/'),
    addEarning: (data) => handleAPIRequest('/manage-earning/', 'POST', data),
    updateEarning: (id, data) => handleAPIRequest(`/manage-earning/${id}/`, 'PUT', data),
};

// Expose globals for pages that rely on these names (backwards compatibility)
if (typeof window !== 'undefined') {
    window.paymentAPI = paymentAPI;
    window.leaveAPI = leaveAPI;
    window.notificationAPI = notificationAPI;
    window.earningsAPI = earningsAPI;
    window.API = {
        payments: paymentAPI,
        leaves: leaveAPI,
        notifications: notificationAPI,
        earnings: earningsAPI,
    };
}
