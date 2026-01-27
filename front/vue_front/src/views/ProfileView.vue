<template>
  <div class="font-inter bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50 text-dark min-h-screen flex flex-col">
    <AppHeader />
    
    <main class="flex-grow container mx-auto px-4 py-8">
      <!-- 页面标题 -->

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <!-- 左侧：头像和基本信息卡片 -->
        <div class="lg:col-span-4 space-y-6">
          <div class="bg-white rounded-2xl shadow-xl shadow-primary/5 overflow-hidden border border-gray-100/50">
            <!-- 头像区域 - 渐变背景 -->
            <div class="relative bg-gradient-to-br from-primary via-blue-500 to-indigo-600 px-6 py-10">
              <!-- 装饰图案 -->
              <div class="absolute inset-0 opacity-10">
                <div class="absolute top-4 left-4 w-20 h-20 border-2 border-white rounded-full"></div>
                <div class="absolute bottom-4 right-4 w-32 h-32 border-2 border-white rounded-full"></div>
                <div class="absolute top-1/2 right-8 w-8 h-8 bg-white rounded-full"></div>
              </div>
              
              <div class="relative text-center">
                <div class="relative inline-block group">
                  <div class="w-28 h-28 rounded-full p-1 bg-white/20 backdrop-blur-sm">
                    <img 
                      :src="avatarUrl" 
                      alt="用户头像" 
                      class="w-full h-full rounded-full object-cover border-4 border-white shadow-lg"
                    >
                  </div>
                  <!-- 上传按钮 - 使用 SVG 图标 -->
                  <label 
                    class="absolute bottom-1 right-1 w-9 h-9 bg-white rounded-full shadow-lg flex items-center justify-center cursor-pointer hover:bg-gray-50 hover:scale-110 transition-all duration-200 group-hover:opacity-100"
                    :class="uploading ? 'opacity-50 cursor-not-allowed' : ''"
                  >
                    <svg v-if="!uploading" class="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    </svg>
                    <svg v-else class="w-4 h-4 text-primary animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <input 
                      type="file" 
                      accept="image/*" 
                      class="hidden" 
                      @change="handleAvatarChange"
                      :disabled="uploading"
                    >
                  </label>
                </div>
                <h3 class="text-xl font-bold text-white mt-5">{{ profile.name || profile.username || '用户' }}</h3>
                <p class="text-white/70 text-sm mt-1.5 flex items-center justify-center gap-1.5">
                  <span class="inline-block w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                  {{ getRoleName(profile.role) }}
                </p>
              </div>
            </div>
            
            <!-- 基本信息列表 -->
            <div class="p-6">
              <div class="space-y-5">
                <div class="flex items-center group">
                  <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center mr-4 group-hover:scale-105 transition-transform">
                    <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2"></path>
                    </svg>
                  </div>
                  <div class="flex-1">
                    <p class="text-xs text-light-dark uppercase tracking-wide">员工编号</p>
                    <p class="font-semibold text-dark mt-0.5">{{ profile.employeeId || '未设置' }}</p>
                  </div>
                </div>
                
                <div class="flex items-center group">
                  <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-50 to-pink-100 flex items-center justify-center mr-4 group-hover:scale-105 transition-transform">
                    <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                    </svg>
                  </div>
                  <div class="flex-1">
                    <p class="text-xs text-light-dark uppercase tracking-wide">所属部门</p>
                    <p class="font-semibold text-dark mt-0.5">{{ profile.department || '未设置' }}</p>
                  </div>
                </div>
                
                <div class="flex items-center group">
                  <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center mr-4 group-hover:scale-105 transition-transform">
                    <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                  </div>
                  <div class="flex-1">
                    <p class="text-xs text-light-dark uppercase tracking-wide">入职时间</p>
                    <p class="font-semibold text-dark mt-0.5">{{ profile.joinDate || '未设置' }}</p>
                  </div>
                </div>
                
                <div class="flex items-center group">
                  <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-50 to-orange-100 flex items-center justify-center mr-4 group-hover:scale-105 transition-transform">
                    <svg class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                    </svg>
                  </div>
                  <div class="flex-1">
                    <p class="text-xs text-light-dark uppercase tracking-wide">账户角色</p>
                    <span 
                      class="inline-block mt-1 px-3 py-1 text-xs font-medium rounded-full"
                      :class="getRoleBadgeClass(profile.role)"
                    >
                      {{ getRoleName(profile.role) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 安全设置卡片 - 移到左侧 -->
          <div class="bg-white rounded-2xl shadow-xl shadow-primary/5 overflow-hidden border border-gray-100/50">
            <div class="px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-gray-50/50 to-white">
              <h3 class="text-lg font-bold text-dark">安全设置</h3>
              <p class="text-sm text-light-dark mt-0.5">管理您的账户安全</p>
            </div>
            
            <div class="p-6">
              <!-- 修改密码 -->
              <div class="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50/50 to-indigo-50/50 rounded-xl border border-blue-100/50 hover:shadow-md transition-all">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-gradient-to-br from-primary to-blue-600 rounded-xl flex items-center justify-center mr-4 shadow-lg shadow-primary/20">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                    </svg>
                  </div>
                  <div>
                    <h4 class="font-bold text-dark text-sm">登录密码</h4>
                    <p class="text-xs text-light-dark mt-0.5">定期更换密码可提高账户安全性</p>
                  </div>
                </div>
                <button 
                  @click="showPasswordModal = true"
                  class="px-4 py-2 text-sm font-medium bg-white border-2 border-primary text-primary rounded-xl hover:bg-primary hover:text-white transition-all shadow-sm whitespace-nowrap"
                >
                  修改
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 右侧：编辑表单 -->
        <div class="lg:col-span-8">
          <!-- 编辑资料卡片 -->
          <div class="bg-white rounded-2xl shadow-xl shadow-primary/5 overflow-hidden border border-gray-100/50">
            <div class="px-8 py-5 border-b border-gray-100 flex items-center justify-between bg-gradient-to-r from-gray-50/50 to-white">
              <div>
                <h3 class="text-lg font-bold text-dark">编辑资料</h3>
                <p class="text-sm text-light-dark mt-0.5">更新您的个人信息</p>
              </div>
              <span 
                v-if="hasChanges"
                class="flex items-center text-sm text-amber-600 bg-amber-50 px-3 py-1.5 rounded-full"
              >
                <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
                有未保存的更改
              </span>
            </div>
            
            <form @submit.prevent="handleSubmit" class="p-8">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                <!-- 用户名（只读） -->
                <div class="space-y-2 md:col-span-2">
                  <label class="block text-sm font-semibold text-dark">
                    用户名 
                    <span class="text-light-dark font-normal text-xs ml-1">(不可修改)</span>
                  </label>
                  <div class="relative">
                    <input 
                      type="text" 
                      :value="profile.username"
                      disabled
                      class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50/80 text-light-dark cursor-not-allowed pl-11"
                    >
                    <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                    </svg>
                  </div>
                </div>
                
                <!-- 邮箱 -->
                <div class="space-y-2">
                  <label class="block text-sm font-semibold text-dark">邮箱</label>
                  <div class="relative">
                    <input 
                      v-model="formData.email"
                      type="email" 
                      placeholder="请输入邮箱地址"
                      class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all pl-11"
                    >
                    <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                    </svg>
                  </div>
                </div>
                
                <!-- 手机号 -->
                <div class="space-y-2">
                  <label class="block text-sm font-semibold text-dark">手机号</label>
                  <div class="relative">
                    <input 
                      v-model="formData.phone"
                      type="tel" 
                      placeholder="请输入手机号码"
                      class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all pl-11"
                    >
                    <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                    </svg>
                  </div>
                </div>
                
                <!-- 性别 -->
                <div class="space-y-2">
                  <label class="block text-sm font-semibold text-dark">性别</label>
                  <div class="relative">
                    <select 
                      v-model="formData.gender"
                      class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all pl-11 appearance-none bg-white"
                    >
                      <option value="">请选择</option>
                      <option value="男">男</option>
                      <option value="女">女</option>
                      <option value="其他">其他</option>
                    </select>
                    <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                    </svg>
                    <svg class="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                  </div>
                </div>
                
                <!-- 生日 -->
                <div class="space-y-2">
                  <label class="block text-sm font-semibold text-dark">生日</label>
                  <div class="relative">
                    <input 
                      v-model="formData.birthday"
                      type="date" 
                      class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all pl-11"
                    >
                    <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 15.546c-.523 0-1.046.151-1.5.454a2.704 2.704 0 01-3 0 2.704 2.704 0 00-3 0 2.704 2.704 0 01-3 0 2.704 2.704 0 00-3 0 2.704 2.704 0 01-3 0 2.701 2.701 0 00-1.5-.454M9 6v2m6-2v2m-9 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v4a2 2 0 002 2z"></path>
                    </svg>
                  </div>
                </div>
                
                <!-- 个人简介 -->
                <div class="md:col-span-2 space-y-2">
                  <label class="block text-sm font-semibold text-dark">个人简介</label>
                  <textarea 
                    v-model="formData.bio"
                    rows="4"
                    placeholder="介绍一下您自己..."
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-none"
                  ></textarea>
                  <p class="text-xs text-light-dark">最多 200 字</p>
                </div>
              </div>
              
              <!-- 按钮区域 -->
              <div class="flex justify-end gap-4 mt-8 pt-6 border-t border-gray-100">
                <button 
                  type="button"
                  @click="resetForm"
                  class="px-6 py-2.5 border border-gray-200 rounded-xl text-light-dark hover:bg-gray-50 hover:border-gray-300 transition-all font-medium"
                  :disabled="saving"
                >
                  重置
                </button>
                <button 
                  type="submit"
                  class="px-8 py-2.5 bg-gradient-to-r from-primary to-blue-600 text-white rounded-xl hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none disabled:hover:translate-y-0 flex items-center gap-2"
                  :disabled="saving || !hasChanges"
                >
                  <svg v-if="saving" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ saving ? '保存中...' : '保存更改' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </main>
    
    <AppFooter />
    
    <!-- 修改密码模态框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div 
          v-if="showPasswordModal"
          class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          @click.self="showPasswordModal = false"
        >
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden transform">
            <div class="px-6 py-5 border-b border-gray-100 flex items-center justify-between bg-gradient-to-r from-gray-50 to-white">
              <div>
                <h3 class="text-lg font-bold text-dark">修改密码</h3>
                <p class="text-sm text-light-dark mt-0.5">请输入您的新密码</p>
              </div>
              <button 
                @click="showPasswordModal = false"
                class="w-8 h-8 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
              >
                <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <form @submit.prevent="handleChangePassword" class="p-6 space-y-5">
              <div class="space-y-2">
                <label class="block text-sm font-semibold text-dark">当前密码</label>
                <div class="relative">
                  <input 
                    v-model="passwordForm.oldPassword"
                    type="password" 
                    placeholder="请输入当前密码"
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all pl-11"
                    required
                  >
                  <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                  </svg>
                </div>
              </div>
              
              <div class="space-y-2">
                <label class="block text-sm font-semibold text-dark">新密码</label>
                <div class="relative">
                  <input 
                    v-model="passwordForm.newPassword"
                    type="password" 
                    placeholder="请输入新密码（至少6位）"
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all pl-11"
                    required
                  >
                  <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
                  </svg>
                </div>
              </div>
              
              <div class="space-y-2">
                <label class="block text-sm font-semibold text-dark">确认新密码</label>
                <div class="relative">
                  <input 
                    v-model="passwordForm.confirmPassword"
                    type="password" 
                    placeholder="请再次输入新密码"
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all pl-11"
                    required
                  >
                  <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                  </svg>
                </div>
              </div>
              
              <div class="flex justify-end gap-3 pt-4">
                <button 
                  type="button"
                  @click="showPasswordModal = false"
                  class="px-5 py-2.5 border border-gray-200 rounded-xl text-light-dark hover:bg-gray-50 transition-all font-medium"
                >
                  取消
                </button>
                <button 
                  type="submit"
                  class="px-5 py-2.5 bg-gradient-to-r from-primary to-blue-600 text-white rounded-xl hover:shadow-lg hover:shadow-primary/25 transition-all font-medium disabled:opacity-50 flex items-center gap-2"
                  :disabled="changingPassword"
                >
                  <svg v-if="changingPassword" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ changingPassword ? '提交中...' : '确认修改' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>
    
    <Toast ref="toastRef" :message="toastMessage" :type="toastType" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import Toast from '@/components/Toast.vue'

// API 导入
import { getUserProfile, updateUserProfile, uploadAvatar, type UserProfile, type UpdateProfileParams } from '@/api/user'
import request from '@/api/request'

// Toast 相关
const toastRef = ref<InstanceType<typeof Toast> | null>(null)
const toastMessage = ref('')
const toastType = ref<'success' | 'warning'>('success')

// 状态
const loading = ref(true)
const saving = ref(false)
const uploading = ref(false)
const showPasswordModal = ref(false)
const changingPassword = ref(false)

// 用户资料
const profile = reactive<UserProfile>({
  id: '',
  username: '',
  name: '',
  email: '',
  phone: '',
  avatar: '',
  gender: '',
  birthday: '',
  bio: '',
  role: '',
  department: '',
  employeeId: '',
  joinDate: ''
})

// 表单数据
const formData = reactive<UpdateProfileParams>({
  email: '',
  phone: '',
  gender: '',
  birthday: '',
  bio: ''
})

// 密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 计算头像 URL
const avatarUrl = computed(() => {
  if (profile.avatar) {
    if (profile.avatar.startsWith('/')) {
      return `http://localhost:5000${profile.avatar}`
    }
    return profile.avatar
  }
  return 'https://picsum.photos/id/1005/200/200'
})

// 检查是否有更改
const hasChanges = computed(() => {
  return (
    formData.email !== profile.email ||
    formData.phone !== profile.phone ||
    formData.gender !== profile.gender ||
    formData.birthday !== profile.birthday ||
    formData.bio !== profile.bio
  )
})

// 获取角色名称
const getRoleName = (role: string) => {
  const roleMap: Record<string, string> = {
    'manager': '管理员',
    'user': '普通用户',
    'vip_user': 'VIP用户',
    'admin': '超级管理员'
  }
  return roleMap[role] || role || '普通用户'
}

// 获取角色徽章样式
const getRoleBadgeClass = (role: string) => {
  switch (role) {
    case 'admin':
      return 'bg-gradient-to-r from-red-500 to-pink-500 text-white'
    case 'manager':
      return 'bg-gradient-to-r from-primary to-blue-600 text-white'
    case 'vip_user':
      return 'bg-gradient-to-r from-amber-400 to-orange-500 text-white'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}

// 显示 Toast
const showToast = (message: string, type: 'success' | 'warning' = 'success') => {
  toastMessage.value = message
  toastType.value = type
  toastRef.value?.show()
}

// 获取用户资料
const fetchProfile = async () => {
  loading.value = true
  try {
    const { data: res } = await getUserProfile()
    if (res.code === 200 && res.data) {
      Object.assign(profile, res.data)
      formData.email = res.data.email || ''
      formData.phone = res.data.phone || ''
      formData.gender = res.data.gender || ''
      formData.birthday = res.data.birthday || ''
      formData.bio = res.data.bio || ''
    }
  } catch (error) {
    console.error('获取用户资料失败:', error)
    showToast('获取用户资料失败', 'warning')
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.email = profile.email || ''
  formData.phone = profile.phone || ''
  formData.gender = profile.gender || ''
  formData.birthday = profile.birthday || ''
  formData.bio = profile.bio || ''
}

// 提交表单
const handleSubmit = async () => {
  if (!hasChanges.value) return
  
  saving.value = true
  try {
    const { data: res } = await updateUserProfile(formData)
    if (res.code === 200) {
      Object.assign(profile, res.data)
      showToast('资料更新成功')
    } else {
      showToast(res.message || '更新失败', 'warning')
    }
  } catch (error) {
    console.error('更新资料失败:', error)
    showToast('更新资料失败', 'warning')
  } finally {
    saving.value = false
  }
}

// 处理头像更换
const handleAvatarChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  
  if (!file) return
  
  if (!file.type.startsWith('image/')) {
    showToast('请选择图片文件', 'warning')
    return
  }
  
  if (file.size > 5 * 1024 * 1024) {
    showToast('图片大小不能超过 5MB', 'warning')
    return
  }
  
  uploading.value = true
  try {
    const { data: res } = await uploadAvatar(file)
    if (res.code === 200 && res.data) {
      profile.avatar = res.data.avatar
      showToast('头像上传成功')
    } else {
      showToast(res.message || '上传失败', 'warning')
    }
  } catch (error) {
    console.error('上传头像失败:', error)
    showToast('上传头像失败', 'warning')
  } finally {
    uploading.value = false
    input.value = ''
  }
}

// 修改密码
const handleChangePassword = async () => {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    showToast('两次输入的密码不一致', 'warning')
    return
  }
  
  if (passwordForm.newPassword.length < 6) {
    showToast('新密码长度至少为 6 位', 'warning')
    return
  }
  
  changingPassword.value = true
  try {
    const { data: res } = await request.post('/auth/change-password', {
      oldPassword: passwordForm.oldPassword,
      newPassword: passwordForm.newPassword
    })
    
    if (res.code === 200) {
      showToast('密码修改成功')
      showPasswordModal.value = false
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
    } else {
      showToast(res.message || '密码修改失败', 'warning')
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    showToast('修改密码失败', 'warning')
  } finally {
    changingPassword.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
/* 模态框动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .bg-white,
.modal-leave-to .bg-white {
  transform: scale(0.9) translateY(20px);
}
</style>
