document.addEventListener("DOMContentLoaded", () => {
	document.getElementById("call-api").onclick = async () => {
		const response = await fetch("/api/hello?name=User");
		const data = await response.json();
		document.getElementById("output").textContent = data.message;
	};
});
