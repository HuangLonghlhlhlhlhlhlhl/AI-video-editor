import re

with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Remove the left aside entirely
html = re.sub(r'<!-- SideNavBar -->\s*<aside class="fixed left-0 top-10 bottom-12 flex flex-col items-center py-4 w-16 z-40 bg-\[#1C1C1C\] border-r border-\[#FFFFFF15\]">.*?</aside>\s*', '', html, flags=re.DOTALL)

# Update main grid to full width
html = html.replace('main class="ml-16 w-full h-[calc(100vh-88px)] grid grid-cols-12 grid-rows-12 gap-[2px] bg-[#0A0A0A] p-[2px]"', 'main class="w-full h-[calc(100vh-88px)] grid grid-cols-12 grid-rows-12 gap-[2px] bg-[#0A0A0A] p-[2px]"')

# Replace the Asset Library folder button
old_folder_btn = """<button id="browse-btn" class="material-symbols-outlined text-gray-500 text-sm hover:text-white transition-colors cursor-pointer" title="添加文件夹">add_folder</button>"""
new_folder_btn = """<!-- CapCut Style Import Area -->
                    <div class="flex items-center text-gray-400 bg-[#2A2A2A] rounded overflow-hidden">
                        <button class="px-2 py-0.5 hover:bg-[#3A3A3A] hover:text-white flex items-center justify-center transition-colors">
                            <span class="material-symbols-outlined text-[16px]">add</span>
                        </button>
                        <div class="w-[1px] h-3 bg-gray-600"></div>
                        <button id="browse-btn" class="px-2 py-0.5 hover:bg-[#3A3A3A] hover:text-white flex items-center justify-center transition-colors">
                            <span class="material-symbols-outlined text-[14px]">folder</span>
                        </button>
                    </div>"""
html = html.replace(old_folder_btn, new_folder_btn)

# Replace the bottom footer completely
old_footer_start = "<!-- BottomNavBar -->"
new_footer = """<!-- BottomNavBar (DaVinci Style) -->
    <footer class="fixed bottom-0 left-0 w-full z-50 flex justify-between items-center h-[52px] px-6 bg-[#181818] border-t border-[#FFFFFF15] shadow-[0_-5px_15px_rgba(0,0,0,0.3)]">
        
        <!-- Left spacer -->
        <div class="flex-1"></div>

        <!-- Center Nav Items -->
        <nav class="flex justify-center items-center h-full space-x-12">
            <button class="flex flex-col items-center group transition-all duration-200 text-gray-500 pt-1.5 hover:text-gray-300">
                <span class="material-symbols-outlined text-[20px]">perm_media</span>
                <span class="font-label-bold text-[11px] mt-0.5">媒体</span>
            </button>
            <button class="flex flex-col items-center group transition-all duration-200 text-gray-500 pt-1.5 hover:text-gray-300">
                <span class="material-symbols-outlined text-[20px]">content_cut</span>
                <span class="font-label-bold text-[11px] mt-0.5">快剪</span>
            </button>
            <!-- Active Tab -->
            <button class="flex flex-col items-center group transition-all duration-200 text-[#3E52FF] pt-1.5 relative">
                <div class="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-[3px] bg-[#3E52FF] rounded-b"></div>
                <span class="material-symbols-outlined text-[20px]">movie_edit</span>
                <span class="font-label-bold text-[11px] mt-0.5">编辑</span>
            </button>
            <button class="flex flex-col items-center group transition-all duration-200 text-gray-500 pt-1.5 hover:text-gray-300">
                <span class="material-symbols-outlined text-[20px]">auto_fix_normal</span>
                <span class="font-label-bold text-[11px] mt-0.5">特效</span>
            </button>
            <button class="flex flex-col items-center group transition-all duration-200 text-gray-500 pt-1.5 hover:text-gray-300">
                <span class="material-symbols-outlined text-[20px]">palette</span>
                <span class="font-label-bold text-[11px] mt-0.5">调色</span>
            </button>
            <button class="flex flex-col items-center group transition-all duration-200 text-gray-500 pt-1.5 hover:text-gray-300">
                <span class="material-symbols-outlined text-[20px]">graphic_eq</span>
                <span class="font-label-bold text-[11px] mt-0.5">音频</span>
            </button>
            <button class="flex flex-col items-center group transition-all duration-200 text-gray-500 pt-1.5 hover:text-gray-300">
                <span class="material-symbols-outlined text-[20px]">ios_share</span>
                <span class="font-label-bold text-[11px] mt-0.5">交付</span>
            </button>
        </nav>

        <!-- Right Settings Gear -->
        <div class="flex-1 flex justify-end items-center relative group">
            <div class="text-gray-500 p-2 hover:text-white hover:bg-[#FFFFFF05] rounded-md transition-all cursor-pointer">
                <span class="material-symbols-outlined">settings</span>
            </div>
            <!-- Settings Dropdown -->
            <div class="absolute right-0 bottom-[40px] w-48 bg-[#1C1C1C] border border-[#FFFFFF15] rounded-md shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-100 z-50">
                <ul class="py-1.5 text-[12px] text-gray-300 font-label-bold text-left">
                    <li class="px-4 py-1.5 hover:bg-[#3E52FF] hover:text-white cursor-pointer flex justify-between items-center"><span>全局设置</span><span class="text-gray-500 group-hover/li:text-gray-300 text-[10px]">⌘,</span></li>
                    <li class="px-4 py-1.5 hover:bg-[#3E52FF] hover:text-white cursor-pointer flex justify-between items-center"><span>快捷键设置</span><span class="text-gray-500 text-[10px]">⌥⌘K</span></li>
                    <div class="h-[1px] bg-[#FFFFFF10] my-1.5 w-[90%] mx-auto"></div>
                    <li class="px-4 py-1.5 hover:bg-[#3E52FF] hover:text-white cursor-pointer flex justify-between items-center"><span>关于 Gravity Edit</span></li>
                </ul>
            </div>
        </div>
    </footer>

    <!-- Export Status Overlay -->
    <div id="scanner-logs" class="fixed bottom-[60px] left-4 z-50 text-xs font-mono-label text-blue-400 opacity-0 transition-opacity bg-black/80 px-3 py-1 rounded"></div>

    <script src="app.js"></script>
</body>
</html>"""

import re
html = re.sub(r'<!-- BottomNavBar -->.*</html>', new_footer, html, flags=re.DOTALL)

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
