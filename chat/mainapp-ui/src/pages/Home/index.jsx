import React from "react";

import { Message } from "../../components";
import "./Home.scss";

const Home = () => (
  <section className="home">
    <Message
     avatar="https://image.flaticon.com/icons/png/512/168/168719.png"
     text="Привееет! Как дела, что нового? Я вот выбиралась в Карелию, смотри какая там красотаааа!"
     date="20:30:45"
     attachments={[
       {
         filename: 'file1.jpg',
         url: 'https://pbs.twimg.com/media/EmXZMcMXIAEXM-L.jpg'
       },
       {
         filename: 'file2.jpg',
         url: 'https://im0-tub-by.yandex.net/i?id=5fb70c9713ecdd27605c29ddd24c9a94-l&n=13'
       },
       {
         filename: 'file3.jpg',
         url: 'https://f.vividscreen.info/soft/5e5df66810b2c5399872eb8f8a64be11/Green-Nature-Landscape-2048x2048.jpg'
       }
     ]}
     />
     <Message
     avatar="https://www.flaticon.com/svg/vstatic/svg/168/168724.svg?token=exp=1620209228~hmac=8323f4025a7e3dc94a93d6086d69059f"
     text="И правда! Очень красиво)"
     date="21:34:05"
     isMe={true}
     />
     <Message
     avatar="https://www.flaticon.com/svg/vstatic/svg/168/168724.svg?token=exp=1620209228~hmac=8323f4025a7e3dc94a93d6086d69059f"
     text="А вот у меня новый жилец :З"
     date="21:34:43"
     isMe={true}
     />
     <Message
     avatar="https://image.flaticon.com/icons/png/512/168/168719.png"
     text="Покажи"
     date="21:35:11"
     />
     <Message
     avatar="https://www.flaticon.com/svg/vstatic/svg/168/168724.svg?token=exp=1620209228~hmac=8323f4025a7e3dc94a93d6086d69059f"
     date="22:03:21"
     isMe={true}
     attachments={[
       {
         filename: 'file1.jpg',
         url: 'https://img1.goodfon.ru/original/2048x2048/6/98/britanec-kot-trava-morda-glaza.jpg'
       }
     ]}
     />
     <Message
     avatar="https://www.flaticon.com/svg/vstatic/svg/168/168724.svg?token=exp=1620209228~hmac=8323f4025a7e3dc94a93d6086d69059f"
     text="Антонио"
     date="22:03:29"
     isMe={true}
     />
  </section>
);

export default Home;