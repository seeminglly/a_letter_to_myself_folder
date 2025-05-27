function setRoutine(type) {
    console.log("clicked!", type);  // ✅ 클릭 테스트 로그
    const routineSection = document.getElementById('routine-section');
    const specialSection = document.getElementById('special-section');

    if (type === 'weekly') {
        routineSection.style.display = 'block';
        specialSection.style.display = 'none';
    } else if (type === 'special') {
        routineSection.style.display = 'none';
        specialSection.style.display = 'block';
    }
}


function showCategory(event) {
    let targetTab = event.target;  // ✅ 클릭한 탭 요소 가져오기
    if (!targetTab.dataset.tabTarget) return;  // ✅ data-tab-target이 없으면 종료

    let activeTab = document.querySelector(".tabs .active");  // ✅ 현재 활성화된 탭 찾기
    if (activeTab) {
        activeTab.classList.remove("active");  // ✅ 기존 활성화된 탭에서 active 제거
    }
    targetTab.classList.add("active");  // ✅ 새로 클릭한 탭을 활성화

    // ✅ 모든 편지 섹션 숨기기
    document.querySelectorAll("[data-tab-content]").forEach((section) => {
        section.style.display = "none";
    });

    // ✅ 클릭한 탭과 연결된 편지 섹션만 표시
    let targetSection = document.querySelector(targetTab.dataset.tabTarget);
    if (targetSection) {
        targetSection.style.display = "block";
    }
}

document.addEventListener("DOMContentLoaded", function() {
    let defaultTab = document.querySelector(".tabs .active");  // ✅ 기본 활성화된 탭 찾기
    if (defaultTab) {
        let targetSection = document.querySelector(defaultTab.dataset.tabTarget);
        if (targetSection) {
            targetSection.style.display = "block";  // ✅ 기본 섹션 표시
        }
    }
});




document.addEventListener("DOMContentLoaded", function () {
    const menuButton = document.querySelector(".hamburger-btn"); 
    const menu = document.getElementById("menu"); // 사이드 메뉴
    const pageCover = document.querySelector(".page_cover"); // 배경 어두워지는 영역

    // 햄버거 버튼 클릭 시 메뉴 열기
    menuButton.addEventListener("click", function () {
        document.documentElement.classList.toggle("open");
        menu.classList.toggle("open");
        pageCover.classList.toggle("open");
    });

    // 메뉴 바깥 클릭 시 닫기
    pageCover.addEventListener("click", function () {
        document.documentElement.classList.remove("open");
        menu.classList.remove("open");
        pageCover.classList.remove("open");
    });
});

function toggleDateOptions() {
    var routineType = document.getElementById("routine_type").value;
    document.getElementById("weekly-options").style.display = (routineType === "weekly") ? "block" : "none";
    document.getElementById("monthly-options").style.display = (routineType === "monthly") ? "block" : "none";
}

function redirectToWritePage(){
    alert("오늘의 기분이 '${mood}'로 설정되었습니다. 편지를 작성해보세요!");
    
    var mood = document.getElementById("mood").value;
    
}
function add_routine(){
    alert("루틴이 저장되었습니다!");
}
function add_specialDay(){
    alert("기념일이 저장되었습니다!")
}
document.addEventListener("DOMContentLoaded", function () {
    const tabs = document.querySelectorAll(".tabs li");
    const tabContents = document.querySelectorAll("[data-tab-content]");
    // 초기 상태: "오늘의 편지"만 보이게 설정
    tabContents.forEach(content => content.classList.remove("active"));
    document.querySelector("#today").classList.add("active");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const targetId = tab.getAttribute("data-tab-target");
            const targetContent = document.querySelector(targetId);
            
            if (!targetContent) {
                console.error("탭 콘텐츠를 찾을 수 없습니다:", targetId);
                return;
            }

            // 모든 탭 버튼에서 active 클래스 제거
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");

            // 모든 탭 콘텐츠 숨김
            tabContents.forEach(content => content.classList.remove("active"));
            targetContent.classList.add("active");
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // CSRF 토큰을 쿠키에서 가져오는 함수 (Django의 기본 방식)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const deleteButtons = document.querySelectorAll('.delete-letter-btn');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            // 중요: 이 버튼이 .modalList (li) 내부에 있다면,
            // li를 클릭했을 때 모달이 열리는 동작이 있을 수 있습니다.
            // 삭제 버튼 클릭 시에는 모달 열림을 방지하기 위해 이벤트 전파를 중단합니다.
            event.stopPropagation(); 

            const letterId = this.dataset.letterId;
            if (confirm('정말로 이 편지를 삭제하시겠습니까? 삭제 후에는 복구할 수 없습니다.')) {
                // CSRF 토큰 가져오기 (getCookie 함수 또는 페이지 내 input 태그에서)
                const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;

                if (!csrfToken) {
                    alert('CSRF 토큰을 찾을 수 없습니다. 페이지를 새로고침하고 다시 시도해주세요.');
                    console.error('CSRF token not found.');
                    return;
                }

                fetch(`/letters/delete/${letterId}/`, { // ✅ API URL이 정확한지 확인하세요.
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json',
                        'Accept': 'application/json' // 서버가 JSON 응답을 보내도록 요청
                    }
                })
                .then(response => {
                    if (response.status === 200) { // No Content 성공 (서버에서 내용 없이 성공 응답)
                        return { status: 'success', message: '편지가 성공적으로 삭제되었습니다.' };
                    }
                    // 그 외 경우, JSON 응답을 파싱 시도
                    return response.json().then(data => {
                        if (!response.ok) {
                            // 서버에서 에러 응답 (4xx, 5xx)을 보냈고, JSON 본문이 있는 경우
                            throw new Error(data.message || `서버 오류: ${response.status}`);
                        }
                        return data; // 성공적인 JSON 응답 (예: {status: 'success', message: '...'})
                    });
                })
                .then(data => {
                    if (data.status === 'success') {
                        alert(data.message);
                        // 성공 시 페이지 새로고침 또는 해당 편지 항목 DOM에서 제거
                        // 예: this.closest('li').remove(); // 버튼의 가장 가까운 li 요소를 제거 (동적 처리)
                        window.location.reload(); // 간단하게 페이지 전체 새로고침
                    } else {
                        // data.status가 'error'이거나, 예상치 못한 성공 응답 형식일 경우
                        alert('오류: ' + (data.message || '알 수 없는 오류가 발생했습니다.'));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('편지 삭제 중 오류가 발생했습니다: ' + error.message);
                });
            }
        });
    });
});