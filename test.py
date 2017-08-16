foodlist_file = open('foodlist.txt','r')
food_list = foodlist_file.read().split(',')
food_li
foodlist_file.write(food_list.join(','))
foodlist_file.close()