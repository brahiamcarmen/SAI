navigator.mediaDevices.getUserMedia({ audio: false, video: true}).then((stream)=>{
	console.log(stream)
	let video = document.getElementById('video')
	video.srcObject = stream
}).catch((err)=>console.log(err))