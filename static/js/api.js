// Generic API handler with consistent response format
const handleAPIRequest = async (url, method = 'GET', data = null) => {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data) {
            if (data instanceof FormData) {
                options.body = data;
                delete options.headers['Content-Type'];
            } else {
                options.body = JSON.stringify(data);
            }
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

// API Endpoints
const API = {
    auth: {
        login: (data) => handleAPIRequest('/login/', 'POST', data),
        logout: () => handleAPIRequest('/logout/', 'POST'),
    },

    students: {
        getAll: () => handleAPIRequest('/getStudentData/'),
        getById: (id) => handleAPIRequest(`/getStudentData/${id}/`),
        add: (data) => handleAPIRequest('/manage-student/', 'POST', data),
        update: (id, data) => handleAPIRequest(`/manage-student/${id}/`, 'PUT', data),
        delete: (id) => handleAPIRequest(`/manage-student/${id}/`, 'DELETE'),
    },

    instructors: {
        getAll: () => handleAPIRequest('/getInstructorData/'),
        getById: (id) => handleAPIRequest(`/getInstructorData/${id}/`),
        add: (data) => handleAPIRequest('/manage-instructor/', 'POST', data),
        update: (id, data) => handleAPIRequest(`/manage-instructor/${id}/`, 'PUT', data),
        delete: (id) => handleAPIRequest(`/manage-instructor/${id}/`, 'DELETE'),
    },

    branches: {
        getAll: () => handleAPIRequest('/getBranchData/'),
        getById: (id) => handleAPIRequest(`/getBranchData/${id}/`),
        add: (data) => handleAPIRequest('/manage-branch/', 'POST', data),
        update: (id, data) => handleAPIRequest(`/manage-branch/${id}/`, 'PUT', data),
        delete: (id) => handleAPIRequest(`/manage-branch/${id}/`, 'DELETE'),
        getAdmins: () => handleAPIRequest('/getBranchAdminData/'),
    },

    vehicles: {
        getAll: () => handleAPIRequest('/getVehicleData/'),
        getById: (id) => handleAPIRequest(`/getVehicleData/${id}/`),
        add: (data) => handleAPIRequest('/manage-vehicle/', 'POST', data),
        update: (id, data) => handleAPIRequest(`/manage-vehicle/${id}/`, 'PUT', data),
        delete: (id) => handleAPIRequest(`/manage-vehicle/${id}/`, 'DELETE'),
    },

    attendance: {
        getAll: () => handleAPIRequest('/getAttendanceData/'),
        getByStudent: (studentId) => handleAPIRequest(`/getAttendanceData/?studentId=${studentId}`),
        add: (data) => handleAPIRequest('/manage-attendance/', 'POST', data),
        update: (id, data) => handleAPIRequest(`/manage-attendance/${id}/`, 'PUT', data),
        delete: (id) => handleAPIRequest(`/manage-attendance/${id}/`, 'DELETE'),
    },

    complains: {
        getAll: () => handleAPIRequest('/getComplainData/'),
        getById: (id) => handleAPIRequest(`/getComplainData/${id}/`),
        add: (data) => handleAPIRequest('/manage-complain/', 'POST', data),
        update: (id, data) => handleAPIRequest(`/manage-complain/${id}/`, 'PUT', data),
        resolve: (id) => handleAPIRequest(`/resolve-complain/${id}/`, 'PUT'),
    },

    payments: {
        getAll: () => handleAPIRequest('/getPaymentData/'),
        getRemaining: () => handleAPIRequest('/getReamainingPaymentData/'),
        add: (data) => handleAPIRequest('/manage-payment/', 'POST', data),
        update: (id, data) => handleAPIRequest(`/manage-payment/${id}/`, 'PUT', data),
    },

    notifications: {
        getAll: () => handleAPIRequest('/getNotificationData/'),
        markAsRead: (id) => handleAPIRequest(`/manage-Notification/${id}/`, 'PUT'),
    },

    earnings: {
        getAll: () => handleAPIRequest('/getEearningData/'),
    },

    slots: {
        getAll: () => handleAPIRequest('/getSlotWiseData/'),
        add: (data) => handleAPIRequest('/manage-slot/', 'POST', data),
        update: (id, data) => handleAPIRequest(`/manage-slot/${id}/`, 'PUT', data),
        delete: (id) => handleAPIRequest(`/manage-slot/${id}/`, 'DELETE'),
    },

    dlInfo: {
        getAll: () => handleAPIRequest('/getDlInfoData/'),
        add: (data) => handleAPIRequest('/manage-dlinfo/', 'POST', data),
        update: (id, data) => handleAPIRequest(`/manage-dlinfo/${id}/`, 'PUT', data),
        delete: (id) => handleAPIRequest(`/manage-dlinfo/${id}/`, 'DELETE'),
    },
};

// UI Helper functions
const showModal = (modalId, success, message) => {
    const modal = document.getElementById(modalId);
    const msgElement = modal.querySelector(".message") || modal.querySelector("[id$='-message']");
    const headingElement = modal.querySelector(".heading") || modal.querySelector("[id$='-heading']");

    modal.classList.remove('scale-0', 'opacity-0');
    modal.classList.add('scale-100', 'opacity-100');

    if (msgElement) msgElement.innerText = message;
    if (headingElement) headingElement.innerText = success ? "Success" : "Error";
};

const hideModal = (modalId) => {
    const modal = document.getElementById(modalId);
    modal.classList.remove('scale-100', 'opacity-100');
    modal.classList.add('scale-0', 'opacity-0');
};

const refreshTable = (gridInstance) => {
    if (gridInstance && typeof gridInstance.forceRender === 'function') {
        gridInstance.forceRender();
    }
};

// Export utilities
window.API = API;
window.showModal = showModal;
window.hideModal = hideModal;
window.refreshTable = refreshTable;

// Add backward-compatible global aliases (used by templates/index.html and other pages)
window.paymentAPI = {
    getPayments: API.payments.getAll,
    getRemaining: API.payments.getRemaining,
    addPayment: API.payments.add,
    updatePayment: API.payments.update,
    deletePayment: API.payments.delete,
};

window.notificationAPI = {
    getNotifications: API.notifications.getAll,
    markAsRead: API.notifications.markAsRead,
    deleteNotification: API.notifications.delete,
};

window.earningsAPI = {
    getEarnings: API.earnings.getAll,
    addEarning: API.earnings.add || (() => Promise.reject(new Error('Not implemented'))),
    updateEarning: API.earnings.update || (() => Promise.reject(new Error('Not implemented'))),
};

window.leaveAPI = {
    getLeaves: API.leaves ? API.leaves.getAll : () => handleAPIRequest('/getStudentOnLeaveData/'),
    addLeave: API.leaves ? API.leaves.add : (data) => handleAPIRequest('/manage-leave/', 'POST', data),
    updateLeave: API.leaves ? API.leaves.update : (id, data) => handleAPIRequest(`/manage-leave/${id}/`, 'PUT', data),
    deleteLeave: API.leaves ? API.leaves.delete : (id) => handleAPIRequest(`/manage-leave/${id}/`, 'DELETE'),
};
