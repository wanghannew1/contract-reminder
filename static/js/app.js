/**
 * 合同提醒管理系统 - Alpine.js 应用逻辑
 * ======================================
 */

// ==========================================
// Dashboard Component
// ==========================================
function dashboardStats() {
    return {
        stats: {
            total: 0,
            active: 0,
            expiring_soon: 0,
            expired: 0
        },
        init() {
            // 初始化仪表盘统计数据
            this.loadStats();
        },
        loadStats() {
            // 可通过fetch从API获取数据
            // 目前由后端直接渲染
        }
    };
}

// ==========================================
// Contract Search Component
// ==========================================
function contractSearch() {
    return {
        search: '',
        status: '',
        contract_type: '',
        date_from: '',
        date_to: '',
        filter: '',

        init() {
            // 从URL参数初始化搜索条件
            const params = new URLSearchParams(window.location.search);
            this.search = params.get('search') || '';
            this.status = params.get('status') || '';
            this.contract_type = params.get('contract_type') || '';
            this.date_from = params.get('date_from') || '';
            this.date_to = params.get('date_to') || '';
            this.filter = params.get('filter') || '';
        },

        clearFilters() {
            this.search = '';
            this.status = '';
            this.contract_type = '';
            this.date_from = '';
            this.date_to = '';
            this.filter = '';
            this.submitForm();
        },

        submitForm() {
            const form = document.getElementById('searchForm');
            if (form) form.submit();
        }
    };
}

// ==========================================
// Import Form Component
// ==========================================
function importForm() {
    return {
        csv_file: null,
        previewData: [],
        importResult: null,
        uploading: false,
        fileSelected(event) {
            this.csv_file = event.target.files[0];
        },
        submitForm() {
            this.uploading = true;
            const form = event.target;
            const formData = new FormData(form);

            fetch('/contracts/import', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': form.querySelector('[name=csrf_token]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                this.importResult = data;
                this.uploading = false;
                if (data.success) {
                    setTimeout(() => {
                        window.location.href = '/contracts/list';
                    }, 2000);
                }
            })
            .catch(error => {
                console.error('Import error:', error);
                this.importResult = {
                    success: false,
                    message: '导入过程中发生错误，请重试。'
                };
                this.uploading = false;
            });
        }
    };
}

// ==========================================
// Calendar List Component
// ==========================================
function calendarList() {
    return {
        currentView: 'list',
        events: [],

        init() {
            this.loadEvents();
        },

        loadEvents() {
            // 从页面渲染的数据中获取
        },

        toggleView() {
            this.currentView = this.currentView === 'list' ? 'calendar' : 'list';
        }
    };
}

// ==========================================
// User Management Component
// ==========================================
function userManagement() {
    return {
        selectedUsers: [],
        selectAll: false,

        toggleSelectAll() {
            if (this.selectAll) {
                this.selectedUsers = document.querySelectorAll('.user-checkbox').map(cb => cb.value);
            } else {
                this.selectedUsers = [];
            }
        },

        toggleUser(userId) {
            const index = this.selectedUsers.indexOf(userId);
            if (index > -1) {
                this.selectedUsers.splice(index, 1);
            } else {
                this.selectedUsers.push(userId);
            }
        },

        batchDelete() {
            if (this.selectedUsers.length === 0) {
                alert('请先选择要删除的用户');
                return;
            }
            if (confirm(`确定要删除 ${this.selectedUsers.length} 个用户吗？此操作不可恢复。`)) {
                fetch('/admin/users/batch-delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.content || ''
                    },
                    body: JSON.stringify({ users: this.selectedUsers })
                }).then(response => {
                    if (response.ok) {
                        window.location.reload();
                    }
                });
            }
        }
    };
}

// ==========================================
// Settings Component
// ==========================================
function settingsManager() {
    return {
        activeTab: 'general',

        init() {
            // 从hash初始化活动标签
            const hash = window.location.hash;
            if (hash) {
                this.activeTab = hash.substring(1);
            }
        },

        switchTab(tab) {
            this.activeTab = tab;
            window.location.hash = tab;
        },

        testEmailSettings() {
            fetch('/admin/settings/test-email', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrf_token]')?.value || ''
                }
            }).then(response => response.json()).then(data => {
                alert(data.success ? '测试邮件发送成功！' : '测试邮件发送失败：' + data.message);
            });
        },

        testSMTPSettings() {
            const form = document.getElementById('smtpForm');
            if (form) {
                const formData = new FormData(form);
                fetch('/admin/settings/test-smtp', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': form.querySelector('[name=csrf_token]')?.value || ''
                    }
                }).then(response => response.json()).then(data => {
                    alert(data.success ? 'SMTP连接成功！' : 'SMTP连接失败：' + data.message);
                });
            }
        }
    };
}

// ==========================================
// Contract Form Component
// ==========================================
function contractForm() {
    return {
        contract: {},
        errors: {},
        saving: false,

        init() {
            // 初始化合同表单
        },

        validateForm() {
            this.errors = {};

            if (!this.contract.name) {
                this.errors.name = '合同名称为必填项';
            }

            if (!this.contract.party) {
                this.errors.party = '签约方为必填项';
            }

            if (!this.contract.start_date) {
                this.errors.start_date = '开始日期为必填项';
            }

            if (!this.contract.end_date) {
                this.errors.end_date = '到期日期为必填项';
            }

            if (this.contract.start_date && this.contract.end_date) {
                if (new Date(this.contract.start_date) > new Date(this.contract.end_date)) {
                    this.errors.end_date = '到期日期必须晚于开始日期';
                }
            }

            return Object.keys(this.errors).length === 0;
        },

        submitForm() {
            if (!this.validateForm()) {
                return false;
            }

            this.saving = true;
            const form = document.getElementById('contractForm');
            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': form.querySelector('[name=csrf_token]')?.value || ''
                }
            }).then(response => {
                if (response.ok) {
                    window.location.href = response.url || '/contracts/list';
                } else {
                    this.saving = false;
                }
            });

            return false;
        }
    };
}

// ==========================================
// Calendar Event Form Component
// ==========================================
function eventForm() {
    return {
        event: {},
        errors: {},

        init() {
            // 初始化事件表单
        },

        validateForm() {
            this.errors = {};

            if (!this.event.title) {
                this.errors.title = '日程标题为必填项';
            }

            if (!this.event.due_date) {
                this.errors.due_date = '日期为必填项';
            }

            return Object.keys(this.errors).length === 0;
        },

        submitForm() {
            if (!this.validateForm()) {
                return false;
            }

            const form = document.getElementById('eventForm');
            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': form.querySelector('[name=csrf_token]')?.value || ''
                }
            }).then(response => {
                if (response.ok) {
                    window.location.href = response.url || '/calendar/list';
                }
            });

            return false;
        }
    };
}

// ==========================================
// FullCalendar Integration
// ==========================================
function initCalendar() {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,listWeek'
        },
        buttonText: {
            today: '今天',
            month: '月',
            week: '周',
            list: '列表'
        },
        locale: 'zh-cn',
        height: 600,
        events: '/calendar/api/events',
        eventClick: function(info) {
            window.location.href = '/calendar/' + info.event.id + '/detail';
        },
        eventRender: function(info) {
            // 自定义事件渲染
        }
    });

    calendar.render();
}

// ==========================================
// Global Utility Functions
// ==========================================

// 确认删除
function confirmDelete(id, name, type) {
    const messages = {
        contract: `确定要删除合同 "${name}" 吗？此操作不可恢复。`,
        event: `确定要删除日程 "${name}" 吗？此操作不可恢复。`,
        user: `确定要删除用户 "${name}" 吗？此操作不可恢复。`
    };

    if (confirm(messages[type] || `确定要删除 "${name}" 吗？此操作不可恢复。`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/${type}s/${id}/delete`;

        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = document.querySelector('meta[name=csrf-token]')?.content ||
                         document.querySelector('[name=csrf_token]')?.value || '';
        form.appendChild(csrfInput);

        document.body.appendChild(form);
        form.submit();
    }
}

// 显示/隐藏密码
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.type = input.type === 'password' ? 'text' : 'password';
    }
}

// 格式化日期
function formatDate(date, format = 'YYYY-MM-DD') {
    if (!date) return '';

    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');

    if (format === 'YYYY-MM-DD') {
        return `${year}-${month}-${day}`;
    } else if (format === 'DD/MM/YYYY') {
        return `${day}/${month}/${year}`;
    } else if (format === 'MM/DD/YYYY') {
        return `${month}/${day}/${year}`;
    }

    return `${year}-${month}-${day}`;
}

// 显示通知消息
function showNotification(message, type = 'info') {
    const alerts = document.querySelector('.alerts-container');
    if (!alerts) return;

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    alerts.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// 导出表格为CSV
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const rows = table.querySelectorAll('tr');
    const csv = [];

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];

        cols.forEach(col => {
            // 跳过操作列
            if (!col.classList.contains('actions')) {
                rowData.push('"' + col.innerText.replace(/"/g, '""') + '"');
            }
        });

        csv.push(rowData.join(','));
    });

    const csvContent = csv.join('\n');
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename + '.csv';
    link.click();
}

// ==========================================
// Document Ready Handler
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 初始化Popover
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // 自动隐藏警告框
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // 表格排序图标切换
    document.querySelectorAll('th a').forEach(link => {
        link.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon) {
                document.querySelectorAll('th a i').forEach(i => {
                    if (i !== icon) {
                        i.classList.remove('bi-caret-up-fill', 'bi-caret-down-fill');
                    }
                });
            }
        });
    });
});

// ==========================================
// Global Error Handler
// ==========================================
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});

// ==========================================
// API Helper Functions
// ==========================================
const API = {
    get(url) {
        return fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        }).then(response => response.json());
    },

    post(url, data) {
        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(data)
        }).then(response => response.json());
    },

    put(url, data) {
        return fetch(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(data)
        }).then(response => response.json());
    },

    delete(url) {
        return fetch(url, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        }).then(response => response.json());
    }
};

// 获取CSRF Token
function getCsrfToken() {
    return document.querySelector('meta[name=csrf-token]')?.content ||
           document.querySelector('[name=csrf_token]')?.value || '';
}

// ==========================================
// Alpine.js Global Handlers
// ==========================================
document.addEventListener('alpine:init', function() {
    // 全局Alpine初始化
});
