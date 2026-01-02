let menu = document.querySelector("#menu-icon");
let navbar = document.querySelector(".navbar");

menu.onclick =() => {
    menu.classList.toggle('bx-x');
    menu.classList.toggle("active");
}

window.onscroll = () => {
    menu.classList.remove('bx-x');
    menu.classList.remove("active");
}

const typed = new typed('.multiple-text',{
    strings : ['Physical Fitness','Weight Gain Strength', 'Training','Fat Lose','Wight Lifting','Running'],
    typeSpeed: 50,
    backspeed: 60,
    backDelay : 1000,
    loop: true,
})


