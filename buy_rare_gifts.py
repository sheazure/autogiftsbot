async def buy_rare_gifts(rare_gifts : list, bot : Bot):

    while True:
        async with aiosqlite.connect('database.sqlite3') as db:
            to_remove = []
            for gift in rare_gifts:
                users = await db.execute("SELECT * FROM users")
                users = await users.fetchall()
                while True:
                    bought_gifts = 0
                    for user in users:
                        balance = user[6]
                        down_stars_limit = int(user[7].split("-")[0])
                        up_stars_limit = int(user[7].split('-')[1])
                        supply_limit = user[8]

                        if balance >= gift["star_count"] and down_stars_limit <= gift["star_count"] <= up_stars_limit and gift["total_count"] <= supply_limit:
                            try:
                                if user[11] != None:
                                    await bot.send_gift(gift_id=gift["id"], chat_id=user[11], text="Приобретено с помощью Gifts Haunter") 
                                else:
                                    await bot.send_gift(gift_id=gift["id"], user_id=user[0], text="Приобретено с помощью Gifts Haunter")
                            except Exception as e:
                                logger.exception(f"{e}")
                                print(f"Ошибка покупки {e}")
                                await bot.send_message(1404205394, f"Ошибка покупки {e}", disable_notification=True)
                            else:
                                bought_gifts += 1
                                await db.execute("UPDATE users SET balance=balance-?, gifts_amount=gifts_amount+1 WHERE user_id=?", (gift["star_count"], user[0]))
                                await db.commit()
                                logger.info(f"Successful gift for {user[2]} (@{user[1]}) ({gift["id"]})")

                    if bought_gifts == 0: # Не куплено ни одного подарка (ни у кого нет денег, либо закочился подарок)
                        to_remove.append(gift)
                        break
            for gift in to_remove:
                rare_gifts.remove(gift)         
        if len(rare_gifts) == 0:
            break
