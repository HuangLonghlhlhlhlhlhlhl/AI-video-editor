document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const scanBtn = document.getElementById('scan-btn');
    const dirInput = document.getElementById('dir-input');
    const browseBtn = document.getElementById('browse-btn');
    const logsContainer = document.getElementById('scanner-logs');
    
    // Views
    const navItems = document.querySelectorAll('.nav-item[data-view]');
    const viewContainers = document.querySelectorAll('.view-container');
    
    // Gallery
    const videoGrid = document.getElementById('video-grid');
    const groupedGrid = document.getElementById('grouped-grid');
    const videoCount = document.getElementById('video-count');
    const refreshBtn = document.getElementById('refresh-btn');
    const searchInput = document.getElementById('search-input');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Smart Edit
    const editPrompt = document.getElementById('edit-prompt');
    const generateEditBtn = document.getElementById('generate-edit-btn');
    const assistantChat = document.getElementById('assistant-chat');
    
    // Timeline & Player
    const mainVideoTrack = document.getElementById('main-video-track');
    const previewPlayer = document.getElementById('preview-player');
    const playerOverlay = document.getElementById('player-overlay');
    const timelineDuration = document.getElementById('timeline-duration');
    const exportBtn = document.getElementById('export-btn');
    const playerTime = document.getElementById('player-time');
    const playPauseIcon = document.getElementById('play-pause-icon');

    if (previewPlayer) {
        previewPlayer.addEventListener('timeupdate', () => {
            if(playerTime) playerTime.textContent = formatTime(previewPlayer.currentTime);
        });
        previewPlayer.addEventListener('play', () => {
            if(playPauseIcon) playPauseIcon.textContent = 'pause';
        });
        previewPlayer.addEventListener('pause', () => {
            if(playPauseIcon) playPauseIcon.textContent = 'play_arrow';
        });
    }

    let allVideos = [];
    let statusInterval = null;

    // --- Navigation & Tabs ---
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            
            const targetView = item.getAttribute('data-view');
            viewContainers.forEach(v => {
                v.style.display = v.id === `view-${targetView}` ? 'flex' : 'none';
            });
        });
    });

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => {
                b.classList.remove('active', 'border-primary', 'text-white', 'bg-surface-container-high');
                b.classList.add('border-transparent', 'text-gray-500');
            });
            btn.classList.add('active', 'border-primary', 'text-white', 'bg-surface-container-high');
            btn.classList.remove('border-transparent', 'text-gray-500');
            
            const targetTab = btn.getAttribute('data-tab');
            tabContents.forEach(c => {
                c.style.display = c.id === `tab-${targetTab}` ? 'block' : 'none';
            });
            
            if (targetTab === 'grouped') {
                fetchGroupedVideos();
            }
        });
    });

    // --- Core Functions ---
    const fetchVideos = async () => {
        try {
            const res = await fetch('/api/videos');
            const data = await res.json();
            allVideos = data.videos || [];
            if(videoCount) videoCount.textContent = allVideos.length;
            renderVideos(allVideos, videoGrid);
        } catch (e) {
            console.error("Failed to fetch videos", e);
        }
    };

    const fetchGroupedVideos = async () => {
        try {
            const res = await fetch('/api/videos/grouped');
            const data = await res.json();
            renderGroupedVideos(data.groups || {});
        } catch (e) {
            console.error("Failed to fetch grouped videos", e);
        }
    };

    // --- Browse & Scan ---
    if(browseBtn) browseBtn.addEventListener('click', async () => {
        if(addChatMessage) addChatMessage("正在唤起系统文件夹选择器...", "ai");
        if (window.pywebview && window.pywebview.api) {
            try {
                const path = await window.pywebview.api.browse_directory();
                if (path) {
                    dirInput.value = path;
                    if(scanBtn) scanBtn.click(); // Automatically trigger scan
                } else {
                    if(addChatMessage) addChatMessage("已取消选择文件夹。", "ai");
                }
            } catch (e) {
                if(addChatMessage) addChatMessage("唤起选择器失败: " + e, "ai");
            }
        } else {
            const promptPath = prompt("原生接口未就绪，请手动输入包含素材的绝对路径：", "/Users/h-l/Desktop/智能视频剪辑");
            if (promptPath) {
                dirInput.value = promptPath;
                if(scanBtn) scanBtn.click();
            }
        }
    });

    if(scanBtn) scanBtn.addEventListener('click', async () => {
        const dir = dirInput.value.trim();
        if (!dir) {
            alert('请输入素材文件夹路径！');
            return;
        }

        scanBtn.disabled = true;
        scanBtn.innerHTML = `
            <span class="material-symbols-outlined text-[18px] animate-spin">sync</span>
            <span class="text-xs">扫描中...</span>
        `;
        logsContainer.innerHTML = '';

        try {
            await fetch('/api/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ directory: dir })
            });

            if (statusInterval) clearInterval(statusInterval);
            statusInterval = setInterval(pollStatus, 1000);
        } catch (e) {
            console.error(e);
            alert('启动扫描失败');
            resetScanState();
        }
    });

    const pollStatus = async () => {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();

            logsContainer.innerHTML = '';
            if (data.logs.length === 0) {
                logsContainer.innerHTML = '<div class="log-placeholder">扫描即将开始...</div>';
            } else {
                data.logs.forEach(log => {
                    const div = document.createElement('div');
                    div.textContent = `[${log.level.toUpperCase()}] ${log.message}`;
                    if (log.level === 'error') div.style.color = '#EF4444';
                    if (log.level === 'success') div.style.color = '#10B981';
                    if (log.level === 'done') div.style.color = '#8B5CF6';
                    logsContainer.appendChild(div);
                });
                logsContainer.scrollTop = logsContainer.scrollHeight;
            }

            if (!data.is_scanning && data.logs.length > 0) {
                clearInterval(statusInterval);
                resetScanState();
                fetchVideos();
            }
        } catch (e) {
            console.error(e);
        }
    };

    const resetScanState = () => {
        if(scanBtn) {
            scanBtn.disabled = false;
            scanBtn.innerHTML = `
                <span class="material-symbols-outlined text-[18px]">sync</span>
                <span class="text-xs">本地扫描</span>
            `;
        }
    };

    // --- Rendering Gallery ---
    const createVideoCard = (v) => {
        const card = document.createElement('div');
        card.className = 'video-card';
        
        const tagsHtml = (v.tags || []).slice(0, 4).map(t => `<span class="tag">${t}</span>`).join('');
        
        let highlightHtml = '';
        if (v.highlights && v.highlights.length > 0) {
            const hl = v.highlights[0];
            highlightHtml = `
                <div class="highlight-box">
                    <div class="highlight-time">${hl.timestamp_start || '00:00'} - ${hl.timestamp_end || '00:05'}</div>
                    <div class="highlight-desc">${hl.description || ''}</div>
                </div>
            `;
        }

        const filename = v.file_path.split('/').pop() || v.file_path;

        card.innerHTML = `
            <div class="video-thumbnail bg-black" style="cursor: pointer; position: relative;" onclick="previewVideo('${encodeURIComponent(v.file_path)}')">
                <video src="/api/media?path=${encodeURIComponent(v.file_path)}#t=1.0" class="w-full h-full object-cover opacity-80 hover:opacity-100" preload="metadata" muted loop onmouseover="this.play()" onmouseout="this.pause()"></video>
            </div>
            <div class="video-content">
                <div class="video-title" title="${v.file_path}">&lrm;${filename}</div>
                <div class="video-desc">${v.description || '无描述'}</div>
                ${highlightHtml}
                <div class="video-tags">
                    ${tagsHtml}
                </div>
            </div>
        `;
        return card;
    };

    const renderVideos = (videos, container) => {
        if(!container) return;
        container.innerHTML = '';
        if (videos.length === 0) {
            container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--text-secondary); padding: 40px;">没有找到素材</div>';
            return;
        }
        videos.forEach(v => container.appendChild(createVideoCard(v)));
    };

    const renderGroupedVideos = (groups) => {
        if(!groupedGrid) return;
        groupedGrid.innerHTML = '';
        const keys = Object.keys(groups);
        
        if (keys.length === 0) {
            groupedGrid.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px;">没有找到分类数据</div>';
            return;
        }

        keys.forEach(groupName => {
            const videos = groups[groupName];
            if (!videos || videos.length === 0) return;

            const section = document.createElement('div');
            section.className = 'group-section';
            
            const title = document.createElement('h3');
            title.className = 'group-title';
            title.textContent = `${groupName} (${videos.length})`;
            
            const grid = document.createElement('div');
            grid.className = 'grid grid-cols-2 gap-2 content-start';
            
            videos.forEach(v => grid.appendChild(createVideoCard(v)));
            
            section.appendChild(title);
            section.appendChild(grid);
            groupedGrid.appendChild(section);
        });
    };

    if(searchInput) searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        if (!query) {
            renderVideos(allVideos, videoGrid);
            return;
        }

        const filtered = allVideos.filter(v => {
            const textMatch = (v.description || '').toLowerCase().includes(query) || 
                              (v.file_path || '').toLowerCase().includes(query);
            const tagMatch = (v.tags || []).some(t => t.toLowerCase().includes(query));
            return textMatch || tagMatch;
        });
        
        renderVideos(filtered, videoGrid);
    });

    // --- Smart Edit & Editor Workspace ---
    const addChatMessage = (text, sender) => {
        const msg = document.createElement('div');
        msg.className = 'flex items-start gap-2 mt-2 ' + (sender === 'user' ? 'flex-row-reverse' : '');
        
        const avatar = document.createElement('div');
        avatar.className = sender === 'user' 
            ? 'w-6 h-6 rounded-full bg-[#353534] flex items-center justify-center flex-shrink-0'
            : 'w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-[0_0_10px_rgba(62,82,255,0.3)]';
        avatar.innerHTML = `<span class="material-symbols-outlined text-white text-[14px]">${sender === 'user' ? 'person' : 'smart_toy'}</span>`;
        
        const bubble = document.createElement('div');
        bubble.className = sender === 'user'
            ? 'bg-primary-container text-on-primary-container p-2.5 rounded-lg rounded-tr-none max-w-[85%] text-[12px] font-body-md leading-relaxed whitespace-pre-wrap'
            : 'bg-surface-container p-2.5 rounded-lg rounded-tl-none border border-outline-variant max-w-[85%] text-[12px] text-zinc-300 font-body-md leading-relaxed whitespace-pre-wrap';
        bubble.textContent = text;
        
        msg.appendChild(avatar);
        msg.appendChild(bubble);
        
        assistantChat.appendChild(msg);
        assistantChat.scrollTop = assistantChat.scrollHeight;
    };

    // Helper: Convert "00:05" or "MM:SS" to seconds
    const parseTime = (timeStr) => {
        if(!timeStr) return 0;
        const parts = timeStr.split(':');
        if(parts.length === 2) {
            return parseInt(parts[0]) * 60 + parseInt(parts[1]);
        }
        return 5; // Default 5 seconds
    };
    
    const formatTime = (seconds) => {
        const h = Math.floor(seconds / 3600).toString().padStart(2, '0');
        const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
        const s = Math.floor(seconds % 60).toString().padStart(2, '0');
        const ms = Math.floor((seconds % 1) * 100).toString().padStart(2, '0');
        return `${h}:${m}:${s}:${ms}`;
    };

    let currentTimeline = [];

    if(generateEditBtn) generateEditBtn.addEventListener('click', async () => {
        const promptText = editPrompt.value.trim();
        if (!promptText) {
            alert('请先输入你的剪辑意图！');
            return;
        }

        addChatMessage(promptText, 'user');
        editPrompt.value = '';
        generateEditBtn.disabled = true;
        
        addChatMessage("正在分析素材并构建时间线，请稍候...", 'ai');

        try {
            const res = await fetch('/api/edit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: promptText })
            });
            const data = await res.json();

            if (data.status === 'error') {
                addChatMessage("抱歉，生成失败：" + data.message, 'ai');
            } else {
                addChatMessage(`生成完毕！【${data.data.title || '草稿'}】\n${data.data.rationale || ''}`, 'ai');
                currentTimeline = data.data.timeline || [];
                renderTimeline(currentTimeline);
            }
        } catch (e) {
            console.error(e);
            addChatMessage("抱歉，系统出现错误。", 'ai');
        } finally {
            generateEditBtn.disabled = false;
        }
    });

    // Make previewVideo accessible globally for the gallery
    window.previewVideo = (encodedPath) => {
        if(!previewPlayer) return;
        playerOverlay.style.display = 'none';
        previewPlayer.classList.remove('hidden');
        previewPlayer.src = `/api/media?path=${encodedPath}`;
        previewPlayer.play();
    };

    const renderTimeline = (timeline) => {
        mainVideoTrack.innerHTML = '';
        if (timeline.length === 0) {
            mainVideoTrack.innerHTML = '<div class="empty-track-msg">没有找到合适的片段...</div>';
            timelineDuration.textContent = "00:00:00";
            return;
        }

        let currentOffset = 0;
        const PIXELS_PER_SECOND = 20; // Scale

        timeline.forEach((item, index) => {
            const startSec = parseTime(item.start_time);
            const endSec = parseTime(item.end_time);
            let duration = endSec - startSec;
            if(duration <= 0) duration = 3; // Fallback
            
            const blockWidth = duration * PIXELS_PER_SECOND;
            const filename = item.file_path ? item.file_path.split('/').pop() : '片段';

            const block = document.createElement('div');
            block.className = 'clip-block';
            block.style.left = `${currentOffset}px`;
            block.style.width = `${blockWidth}px`;
            
            block.innerHTML = `
                <div class="clip-title" title="${filename}">${filename}</div>
                <div class="clip-desc" title="${item.description || ''}">${item.description || ''}</div>
            `;
            
            // Interaction: click to play
            block.addEventListener('click', () => {
                // Remove active from all
                document.querySelectorAll('.clip-block').forEach(b => b.classList.remove('active'));
                block.classList.add('active');
                
                playerOverlay.style.display = 'none';
                previewPlayer.classList.remove('hidden');
                previewPlayer.src = `/api/media?path=${encodeURIComponent(item.file_path)}`;
                // When metadata loaded, jump to start
                previewPlayer.onloadedmetadata = () => {
                    previewPlayer.currentTime = startSec;
                    previewPlayer.play();
                    
                    // Stop playing when it reaches end time
                    const checkEnd = () => {
                        if (previewPlayer.currentTime >= endSec) {
                            previewPlayer.pause();
                            previewPlayer.removeEventListener('timeupdate', checkEnd);
                        }
                    };
                    previewPlayer.addEventListener('timeupdate', checkEnd);
                };
            });

            mainVideoTrack.appendChild(block);
            currentOffset += blockWidth;
            
            // Add margin for transition if any
            if(item.transition) currentOffset += 5; // tiny gap to show transition
        });
        
        timelineDuration.textContent = formatTime(currentOffset / PIXELS_PER_SECOND);
    };

    let exportInterval = null;

    if(exportBtn) exportBtn.addEventListener('click', async () => {
        if (!currentTimeline || currentTimeline.length === 0) {
            alert("时间线为空，请先生成轨道！");
            return;
        }
        
        let outputDir = "";
        if (window.pywebview && window.pywebview.api) {
            outputDir = await window.pywebview.api.browse_directory();
        } else {
            outputDir = prompt("请输入导出文件夹的绝对路径:", "/Users/h-l/Desktop");
        }
        
        if (!outputDir) return;

        exportBtn.disabled = true;
        exportBtn.innerHTML = '正在准备导出...';

        try {
            await fetch('/api/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ timeline: currentTimeline, output_dir: outputDir })
            });

            if (exportInterval) clearInterval(exportInterval);
            exportInterval = setInterval(pollExportStatus, 1000);
        } catch (e) {
            console.error(e);
            alert('导出启动失败');
            resetExportState();
        }
    });

    const pollExportStatus = async () => {
        try {
            const res = await fetch('/api/export/status');
            const data = await res.json();

            if (data.error) {
                alert(data.error);
                clearInterval(exportInterval);
                resetExportState();
                return;
            }

            exportBtn.innerHTML = `渲染中 ${data.progress}% - ${data.status_text}`;

            if (!data.is_exporting && data.progress === 100) {
                clearInterval(exportInterval);
                resetExportState();
                alert(`导出成功！文件已保存至：\n${data.output_file}`);
            }
        } catch (e) {
            console.error(e);
        }
    };

    const resetExportState = () => {
        if(exportBtn) {
            exportBtn.disabled = false;
            exportBtn.innerHTML = '渲染导出';
        }
    };

    // --- Initial Setup ---
    if(refreshBtn) refreshBtn.addEventListener('click', fetchVideos);
    
    fetchVideos();
    pollStatus();
    statusInterval = setInterval(pollStatus, 2000);
});
