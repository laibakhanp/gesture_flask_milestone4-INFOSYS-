 
function updateUI(){
    fetch("/status")
    .then(res => res.json())
    .then(data => {

        document.getElementById("volume-text").innerHTML = data.volume + "%";
        document.getElementById("vol-fill").style.width = data.volume + "%";

        // Gesture Text
        document.getElementById("gesture-name").innerHTML = data.gesture;

        if(data.gesture.includes("Up"))
            document.getElementById("gesture-icon").innerHTML = "⬆";
        else if(data.gesture.includes("Down"))
            document.getElementById("gesture-icon").innerHTML = "⬇";
        else
            document.getElementById("gesture-icon").innerHTML = "✋";

        // Quality Bars
        for(let i=1;i<=5;i++){
            document.getElementById("b"+i).style.background =
                (i <= data.quality) ? "#10b981" : "#475569";
        }

    })
}

setInterval(updateUI, 300);
