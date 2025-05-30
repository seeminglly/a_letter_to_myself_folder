document.addEventListener("DOMContentLoaded", () => {
    const routineForm = document.querySelector("#routine-form-wrapper form");
    const specialForm = document.querySelector("#special-date-form");

    // 공통 CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrfToken = getCookie("csrftoken");

    // 💌 루틴 저장
    routineForm?.addEventListener("submit", (e) => {
        e.preventDefault();
        fetch("http://localhost:8003/routine/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken
            },
            body: new FormData(routineForm)
        })
        .then(res => res.json())
        .then(data => {
            alert("루틴이 저장되었습니다!");
            window.location.reload();  // ✅ 갱신
        })
        .catch(err => {
            alert("루틴 저장 중 오류 발생");
            console.error(err);
        });
    });

    // 🎉 기념일 저장
    specialForm?.addEventListener("submit", (e) => {
        e.preventDefault();
        fetch("http://localhost:8003/routine/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken
            },
            body: new FormData(specialForm)
        })
        .then(res => res.json())
        .then(data => {
            alert("기념일이 저장되었습니다!");
            window.location.reload();
        })
        .catch(err => {
            alert("기념일 저장 중 오류 발생");
            console.error(err);
        });
    });

    // ❌ 루틴 삭제는 나중에 버튼 추가해서 fetch(DELETE)로 연결!
});
