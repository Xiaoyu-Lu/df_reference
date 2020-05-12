# df_reference
CS136 Dom & Xiaoyu
Dialogflow Backend

## Intro
Reference with definite noun phrases (definite NPs) in attraction task-oriented dialog.

## Database Analysis

![img](https://github.com/Xiaoyu-Lu/df_reference/blob/master/app/img/num_of_type.png)

## Demos

```
Hello! How can I help you? My name is DL and I am the virtual assistant of finding attractions in Cambridge.
What type of attractions at what price range are you looking for?
```
```
U1: Are there any cheap nightclubs in town?
A1: I found it! I recommend this one. The Soul Tree Nightclub is in the centre of the Cambridge.
U2: how about boat events?
A2: Wow! I see there are 4 boats that match your needs. Can you add more information to help narrow it down?
U3: the one hosted in the centre
A3: I found two results for you. 
  1) I recommend this one. The Scudamores Punting Co is in the centre of the Cambridge.
  2) I like this one. The The Cambridge Punter is in the centre of the Cambridge as well.
  Which one do you prefer?
U4: tell me more about the latter 
A4: Cool :) The number of The Cambridge Punter is 07807718591. The address is 251a chesterton road.
U5: great. could i have their postcode
A5: sure. Their postcode is CB41AS.
U6: Oh, I also like to know the other one.
A6: Sure. The number of Scudamores Punting Co is 01223359750. The address is granta place, mill lane.
U7: btw, when does the Cambridge Punter open?
A7: ..Here it is: Sorry, the openhours of the The Cambridge Punter is not available.
U8: cool, that's it.
A8: Thank you for using our service.
```
```
U1: i'm looking for a place called kambar
A1: It's located at 1 wheeler street. It's a nightclub in the city's centre and it has a 5 pounds entrance fee. .
U2: Please give me their postcode
A2: Yeah.. Their postcode is CB23QB.
U3: when does it open
A3: ...Here it is: It opens from 10:00 p.m. to 4:00 a.m. depending on whether there is an event on or not.
U4: Great, can you tell me where the scott polar museum is please?
A4: It's located at Lensfield road. It's a museum in the city's centre and there is no entrance fee.
U5: when does it open
A5: Good question. It opens from 10:00 a.m. to 4:00 p.m. from tuesday to saturday.
```


```
U1: is there any free museums in town?
A1: No problem! There are 21 attractions that match your needs. Could you help narrow it down with more information?
U2: the one in the east
A2: I found two results for you. 
   1) I like this one. The Cambridge Artworks is located in the east of the Cambridge. 
   2) Hey, this one is famous. The Gallery At Twelve A High Street is in the east of the Cambridge as well. 
   Which one do you prefer?
U3: the second one please
A3: Nice Choice! The number of Gallery At Twelve A High Street is 01223295264. The address is fulbourn.
U4: Can you give me more information about it?
A4: It's located at Fulbourn. 
    It's a museum in the city's east and it doesn't have an entrance fee..
U5: the other one?
A5: Cool :) The number of Cambridge Artworks is 01223902168. The address is 5 greens road.
U6: when does it open
A6: Yeah.. Sorry, the openhours of the Cambridge Artworks is not available.
U7: I will choose the second one
A7: Cool :) The number of Gallery At Twelve A High Street is 01223295264. The address is fulbourn
U8: tell me more about it.
A8: It's located at Fulbourn. It's a museum in the city's east and it doesn't have an entrance fee..
U9: can i have their postcode
A9: ...Here it is: Their postcode is CB15DH.
U10: thank you
A10: Thank you! We're looking forward to assisting you again.
```


----
*Adapted and builit on the baseline code created by Jialin.*
