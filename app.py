import os
from datetime import date, datetime, timedelta
import pandas as pd
import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="My Food Tracker", page_icon="🥗", layout="centered")

st.markdown("""
<style>
.block-container{max-width:850px;padding-top:1rem;padding-bottom:3rem}
.hero{padding:1.1rem 1.2rem;border-radius:20px;background:linear-gradient(135deg,#eef5ff,#effcf3);border:1px solid #e5ebf2;margin-bottom:1rem}
.hero h1{font-size:2rem;margin:0}.hero p{margin:.3rem 0 0;color:#667085}
div[data-testid="stMetric"]{border:1px solid #e7eaf0;padding:.6rem;border-radius:14px}
div.stButton>button{border-radius:11px;font-weight:600}
</style>
""", unsafe_allow_html=True)

FOODS = [
# name, category, standard quantity, unit, calories, protein, carbs, fat, fiber
("Idli","Breakfast",2,"piece",116,4.0,24,0.6,2.0),
("Mini idli","Breakfast",8,"piece",160,5,32,1,2.5),
("Rava idli","Breakfast",2,"piece",180,5,29,5,2),
("Thatte idli","Breakfast",1,"piece",180,5,36,2,2),
("Plain dosa","Breakfast",1,"piece",168,4,28,4,1.5),
("Masala dosa","Breakfast",1,"piece",300,6,44,11,4),
("Set dosa","Breakfast",2,"piece",260,6,42,7,3),
("Neer dosa","Breakfast",2,"piece",180,3,38,2,1),
("Ragi dosa","Breakfast",2,"piece",240,6,42,5,5),
("Pesarattu","Breakfast",2,"piece",260,14,38,5,8),
("Adai dosa","Breakfast",2,"piece",300,12,42,8,7),
("Uttapam","Breakfast",1,"piece",220,6,35,6,3),
("Onion uttapam","Breakfast",1,"piece",240,6,38,7,3),
("Appam","Breakfast",2,"piece",220,4,46,2,1),
("Puttu","Breakfast",1,"serving",250,5,52,2,4),
("Idiyappam","Breakfast",2,"piece",180,3,39,1,2),
("Akki roti","Breakfast",1,"piece",190,4,34,5,3),
("Ragi mudde","Breakfast",1,"piece",180,4,38,1,5),
("Ven pongal","Breakfast",1,"bowl",280,8,42,8,4),
("Khara bath","Breakfast",1,"bowl",250,5,38,8,4),
("Kesari bath","Breakfast",1,"bowl",300,4,48,11,1),
("Upma","Breakfast",1,"bowl",230,6,36,7,4),
("Avalakki / poha","Breakfast",1,"bowl",220,5,38,6,3),
("Lemon rice","Lunch",1,"bowl",280,5,45,9,3),
("Tamarind rice / puliyogare","Lunch",1,"bowl",320,6,50,11,4),
("Curd rice","Lunch",1,"bowl",260,7,42,6,2),
("Vegetable pulao","Lunch",1,"bowl",280,6,45,8,4),
("Bisibele bath","Lunch",1,"bowl",320,10,50,9,6),
("Tomato bath","Lunch",1,"bowl",270,5,44,7,3),
("Sambar","Side dish",1,"bowl",120,6,18,3,5),
("Rasam","Side dish",1,"bowl",50,2,8,1,1),
("Coconut chutney","Side dish",2,"tbsp",90,1,3,8,1),
("Peanut chutney","Side dish",2,"tbsp",110,4,4,9,2),
("Tomato chutney","Side dish",2,"tbsp",45,1,6,2,1),
("Mint chutney","Side dish",2,"tbsp",30,1,5,1,1),
("Vegetable kurma","Side dish",1,"bowl",180,4,18,10,4),
("Avial","Side dish",1,"bowl",160,4,15,9,5),
("Beans palya","Side dish",1,"bowl",90,3,12,4,5),
("Cabbage palya","Side dish",1,"bowl",80,2,10,4,4),
("Spinach poriyal","Side dish",1,"bowl",100,4,8,6,4),
("Rice, cooked","Staple",1,"bowl",205,4.3,45,0.4,0.6),
("Brown rice, cooked","Staple",1,"bowl",215,5,45,1.8,3.5),
("Chapati","Staple",1,"piece",110,3.5,18,3,3),
("Phulka","Staple",1,"piece",90,3,18,1,2.5),
("Jowar roti","Staple",1,"piece",120,3.5,23,2,3),
("Ragi roti","Staple",1,"piece",150,3.5,28,3,4),
("Dal, cooked","Side dish",1,"bowl",180,11,30,2,8),
("Toor dal","Side dish",1,"bowl",170,10,28,2,7),
("Moong dal","Side dish",1,"bowl",150,10,26,1,7),
("Chana sundal","Snack",1,"bowl",180,9,27,5,7),
("Peanut sundal","Snack",1,"bowl",220,9,14,16,4),
("Boiled chickpeas","Side dish",1,"bowl",210,11,35,3,9),
("Rajma curry","Side dish",1,"bowl",220,12,34,5,9),
("Paneer curry","Side dish",1,"bowl",280,14,12,20,3),
("Egg, boiled","Protein",1,"piece",78,6.3,0.6,5.3,0),
("Egg omelette","Protein",1,"piece",120,7,1,9,0),
("Chicken curry","Protein",1,"bowl",260,24,8,15,2),
("Chicken breast, cooked","Protein",100,"g",165,31,0,3.6,0),
("Fish curry","Protein",1,"bowl",220,22,7,12,1),
("Fish, cooked","Protein",100,"g",180,24,0,9,0),
("Curd","Dairy",1,"bowl",100,5,7,5,0),
("Buttermilk","Drink",1,"glass",60,3,7,2,0),
("Milk","Dairy",1,"glass",150,8,12,8,0),
("Paneer","Dairy",100,"g",265,18,4,20,0),
("Tofu","Dairy alternative",100,"g",145,15,3,8,2),
("Banana","Fruit",1,"piece",105,1.3,27,0.4,3.1),
("Apple","Fruit",1,"piece",95,0.5,25,0.3,4.4),
("Papaya","Fruit",1,"bowl",60,1,15,0.4,2.5),
("Guava","Fruit",1,"piece",68,2.6,14,1,5.4),
("Orange","Fruit",1,"piece",62,1.2,15,0.2,3.1),
("Mango","Fruit",1,"bowl",100,1.4,25,0.6,2.6),
("Tender coconut water","Drink",1,"glass",45,0.5,11,0,0),
("Filter coffee with milk","Drink",1,"cup",80,2,10,3,0),
("Tea with milk","Drink",1,"cup",70,2,10,2.5,0),
("Murukku","Snack",2,"piece",150,3,18,8,1),
("Maddur vada","Snack",1,"piece",180,4,22,8,2),
("Medu vada","Snack",1,"piece",140,4,18,6,2),
("Bajji","Snack",2,"piece",180,4,25,8,3),
("Mysore pak","Sweet",1,"piece",180,2,20,10,0),
("Payasam","Sweet",1,"bowl",220,5,35,7,1),
("Laddu","Sweet",1,"piece",170,3,24,7,2),
("Oats porridge","Breakfast",1,"bowl",200,8,32,5,5),
("Almonds","Snack",10,"piece",70,2.6,2.5,6,1.5),
("Walnuts","Snack",4,"piece",105,2.5,2.2,10.5,1.1),
("Chia seeds","Add-on",1,"tbsp",58,2,5,3.7,4.1),
("Flax seeds","Add-on",1,"tbsp",55,1.9,3,4.3,2.8),
]

def get_client():
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
    key = st.secrets.get("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
    if not url or not key:
        return None
    return create_client(url, key)

def profile_screen():
    st.markdown('<div class="hero"><h1>🥗 My Food Tracker</h1><p>Enter an email address to open your personal food profile.</p></div>', unsafe_allow_html=True)
    with st.form("profile_form"):
        email=st.text_input("Email address", placeholder="you@example.com", key="profile_email")
        submitted=st.form_submit_button("Continue", use_container_width=True)
    if submitted:
        email=email.strip().lower()
        if "@" not in email or "." not in email.split("@")[-1]:
            st.error("Please enter a valid email address.")
        else:
            st.session_state["user_email"]=email
            st.rerun()
    st.caption("No password, signup or email verification is required.")
    st.warning("This is a simple profile selector, not secure authentication. Anyone who enters another person's email address could see that profile's data.")

if not st.session_state.get("user_email"):
    profile_screen()
    st.stop()

user_email=st.session_state["user_email"].strip().lower()
sb=get_client()
if sb is None:
    st.error("Cloud setup is not complete yet. Follow SETUP.md to create a free Supabase project and add its URL and anon key to Streamlit secrets.")
    st.stop()

with st.sidebar:
    st.markdown("### 🥗 My Food Tracker")
    st.write(user_email)
    if st.button("Log out",use_container_width=True):
        for k in ["user_email","selected_food"]:
            st.session_state.pop(k,None)
        st.rerun()
    st.caption("Profile data is separated by the email address you entered.")

st.markdown('<div class="hero"><h1>🥗 My Food Tracker</h1><p>Log South Indian meals, check nutrition, review history and track weight.</p></div>',unsafe_allow_html=True)

tabs=st.tabs(["🍽️ Today","📅 History","⚖️ Weight","🥘 Food list"])
today_tab,history_tab,weight_tab,foods_tab=tabs

def food_df():
    # built-in foods plus user's custom foods
    base=pd.DataFrame(FOODS,columns=["name","category","serving_qty","unit","calories","protein","carbs","fat","fiber"])
    try:
        custom=sb.table("custom_foods").select("*").eq("user_email",user_email).execute().data or []
        if custom:
            cf=pd.DataFrame(custom)
            base=pd.concat([base,cf[["name","category","serving_qty","unit","calories","protein","carbs","fat","fiber"]]],ignore_index=True)
    except Exception:
        pass
    return base.drop_duplicates(subset=["name"],keep="last").sort_values("name").reset_index(drop=True)

def log_rows(start=None,end=None):
    q=sb.table("food_logs").select("*").eq("user_email",user_email)
    if start: q=q.gte("log_date",str(start))
    if end: q=q.lte("log_date",str(end))
    data=q.order("log_date",desc=True).order("created_at",desc=True).execute().data or []
    return pd.DataFrame(data)

def add_food_log(log_date,meal,food_name,qty,unit,base,custom=False):
    factor=float(qty)/float(base["serving_qty"])
    payload={
        "user_email":user_email,"log_date":str(log_date),"meal":meal,"food_name":food_name,
        "quantity":float(qty),"unit":unit,
        "calories":round(float(base["calories"])*factor,2),
        "protein":round(float(base["protein"])*factor,2),
        "carbs":round(float(base["carbs"])*factor,2),
        "fat":round(float(base["fat"])*factor,2),
        "fiber":round(float(base["fiber"])*factor,2),
    }
    sb.table("food_logs").insert(payload).execute()

with today_tab:
    selected_date=st.date_input("Date",date.today(),format="DD/MM/YYYY",key="today_date")
    foods=food_df()
    meal=st.radio("Meal",["Breakfast","Lunch","Dinner","Snacks"],horizontal=True)
    col_food,col_qty=st.columns([2.4,1])
    typed=col_food.text_input("Select or type food",placeholder="Search or type e.g. ragi dosa",key="food_input")
    matches=foods[foods.name.str.contains(typed,case=False,na=False)].head(12) if typed.strip() else foods.head(12)
    chosen=None
    if typed.strip():
        exact=foods[foods.name.str.lower()==typed.strip().lower()]
        if not exact.empty:
            chosen=exact.iloc[0].to_dict()
        elif not matches.empty:
            chosen_name=col_food.selectbox("Matching foods",matches.name.tolist(),label_visibility="collapsed",key="food_match")
            chosen=foods[foods.name==chosen_name].iloc[0].to_dict()
    else:
        chosen_name=col_food.selectbox("Popular foods",matches.name.tolist(),label_visibility="collapsed",key="popular_food")
        chosen=foods[foods.name==chosen_name].iloc[0].to_dict() if not foods.empty else None

    manual_new = bool(typed.strip() and chosen is None and matches.empty)
    if manual_new:
        st.info(f"**{typed.strip()}** is not in the food list yet. Enter the nutrition for the quantity you are logging.")
        mc1,mc2,mc3=st.columns(3)
        new_qty=mc1.number_input("Quantity",min_value=0.1,value=1.0,step=0.5,key="new_food_qty")
        new_unit=mc2.selectbox("Unit",["serving","piece","bowl","g","ml","glass","cup"],key="new_food_unit")
        new_cal=mc3.number_input("Calories",min_value=0.0,value=0.0,step=10.0,key="new_food_cal")
        new_pro=st.number_input("Protein (g)",min_value=0.0,value=0.0,step=0.5,key="new_food_pro")
        new_carbs=st.number_input("Carbs (g)",min_value=0.0,value=0.0,step=1.0,key="new_food_carbs")
        new_fat=st.number_input("Fat (g)",min_value=0.0,value=0.0,step=0.5,key="new_food_fat")
        new_fiber=st.number_input("Fiber (g)",min_value=0.0,value=0.0,step=0.5,key="new_food_fiber")
        save_new=st.checkbox("Save this food for next time",value=True,key="save_new_food")
        if new_cal>0:
            c1,c2=st.columns(2)
            c1.metric("Calories",f"{new_cal:.0f} kcal")
            c2.metric("Protein",f"{new_pro:.1f} g")
        if st.button(f"➕ Add to {meal}",type="primary",use_container_width=True,key="add_manual_new"):
            if new_cal<=0:
                st.error("Enter calories to add this food.")
            else:
                manual_base={"serving_qty":new_qty,"calories":new_cal,"protein":new_pro,"carbs":new_carbs,"fat":new_fat,"fiber":new_fiber}
                try:
                    add_food_log(selected_date,meal,typed.strip(),new_qty,new_unit,manual_base)
                    if save_new:
                        sb.table("custom_foods").insert({
                            "user_email":user_email,"name":typed.strip(),"category":"Other",
                            "serving_qty":new_qty,"unit":new_unit,"calories":new_cal,
                            "protein":new_pro,"carbs":new_carbs,"fat":new_fat,"fiber":new_fiber
                        }).execute()
                    st.success(f"Added {typed.strip()} to {meal}.")
                    st.rerun()
                except Exception:
                    st.error("Could not save this food. It may already exist in your saved foods.")

    if chosen:
        qty=col_qty.number_input(f"Quantity ({chosen['unit']})",min_value=0.1,value=float(chosen["serving_qty"]),step=1.0 if chosen["unit"] in ["piece","tbsp"] else 0.5,key=f"qty_{chosen['name']}_{meal}")
        factor=qty/float(chosen["serving_qty"])
        cal=float(chosen["calories"])*factor
        pro=float(chosen["protein"])*factor
        m1,m2=st.columns(2)
        m1.metric("Calories",f"{cal:.0f} kcal")
        m2.metric("Protein",f"{pro:.1f} g")
        if st.button(f"➕ Add to {meal}",type="primary",use_container_width=True):
            try:
                add_food_log(selected_date,meal,chosen["name"],qty,chosen["unit"],chosen)
                st.session_state["food_input"]=""
                st.success(f"Added {chosen['name']} to {meal}.")
                st.rerun()
            except Exception as e:
                st.error("Could not save the food. Please check the Supabase table setup in SETUP.md.")

    st.divider()
    day=log_rows(selected_date,selected_date)
    st.subheader("Today's meals")
    if day.empty:
        st.info("No food logged for this date yet.")
    else:
        for meal_name,icon in [("Breakfast","🌅"),("Lunch","☀️"),("Dinner","🌙"),("Snacks","🍎")]:
            part=day[day.meal==meal_name]
            with st.container(border=True):
                st.markdown(f"### {icon} {meal_name}")
                if part.empty:
                    st.caption("No food added yet.")
                    continue
                for _,row in part.iterrows():
                    a,b,c,d=st.columns([3,1.1,1.1,.5])
                    a.write(f"**{row.food_name}**")
                    a.caption(f"{row.quantity:g} {row.unit}")
                    b.write(f"{row.calories:.0f} kcal")
                    c.write(f"{row.protein:.1f} g")
                    if d.button("🗑️",key=f"del_{row.id}"):
                        sb.table("food_logs").delete().eq("id",row.id).eq("user_email",user_email).execute()
                        st.rerun()
                st.markdown("---")
                x,y=st.columns(2)
                x.metric(f"{meal_name} calories",f"{part.calories.sum():.0f} kcal")
                y.metric(f"{meal_name} protein",f"{part.protein.sum():.1f} g")
        st.divider()
        x,y,z=st.columns(3)
        x.metric("Daily calories",f"{day.calories.sum():.0f} kcal")
        y.metric("Daily protein",f"{day.protein.sum():.1f} g")
        z.metric("Daily fiber",f"{day.fiber.sum():.1f} g")

with history_tab:
    st.subheader("📅 Food history")
    c1,c2=st.columns(2)
    default_start=date.today()-timedelta(days=30)
    start_date=c1.date_input("From",default_start,key="history_start")
    end_date=c2.date_input("To",date.today(),key="history_end")
    hist=log_rows(start_date,end_date)
    if hist.empty:
        st.info("No food history found for this date range.")
    else:
        hist["log_date"]=pd.to_datetime(hist["log_date"]).dt.date
        summary=hist.groupby("log_date",as_index=False).agg(
            foods=("food_name","count"),calories=("calories","sum"),
            protein=("protein","sum"),fiber=("fiber","sum")
        ).sort_values("log_date",ascending=False)
        st.markdown("#### Daily totals")
        st.dataframe(summary.rename(columns={"log_date":"Date","foods":"Food entries","calories":"Calories (kcal)","protein":"Protein (g)","fiber":"Fiber (g)"}),use_container_width=True,hide_index=True)
        st.markdown("#### Individual food entries")
        view=hist[["log_date","meal","food_name","quantity","unit","calories","protein"]].copy()
        view.columns=["Date","Meal","Food","Quantity","Unit","Calories (kcal)","Protein (g)"]
        st.dataframe(view,use_container_width=True,hide_index=True)
        st.download_button("⬇️ Download history CSV",hist.to_csv(index=False).encode("utf-8"),"food_history.csv","text/csv",use_container_width=True)

with weight_tab:
    st.subheader("⚖️ Weight tracker")
    st.caption("Record your weight regularly to see your trend over time.")
    with st.form("weight_form"):
        weight_date=st.date_input("Date",date.today(),key="weight_date")
        weight_kg=st.number_input("Weight (kg)",min_value=20.0,max_value=350.0,value=60.0,step=0.1)
        note=st.text_input("Note (optional)",placeholder="Morning, before breakfast…")
        save_weight=st.form_submit_button("Save weight",use_container_width=True)
    if save_weight:
        try:
            sb.table("weight_logs").upsert({
                "user_email":user_email,"weight_date":str(weight_date),"weight_kg":float(weight_kg),"note":note.strip()
            },on_conflict="user_email,weight_date").execute()
            st.success("Weight saved.")
            st.rerun()
        except Exception:
            st.error("Could not save weight. Check the weight_logs table setup in SETUP.md.")
    try:
        weights=sb.table("weight_logs").select("*").eq("user_email",user_email).order("weight_date").execute().data or []
        wdf=pd.DataFrame(weights)
        if not wdf.empty:
            wdf["weight_date"]=pd.to_datetime(wdf["weight_date"])
            st.line_chart(wdf.set_index("weight_date")["weight_kg"])
            st.dataframe(wdf[["weight_date","weight_kg","note"]].rename(columns={"weight_date":"Date","weight_kg":"Weight (kg)","note":"Note"}).sort_values("Date",ascending=False),use_container_width=True,hide_index=True)
    except Exception:
        st.info("Weight tracking will be available after the database tables are created.")

with foods_tab:
    st.subheader("🥘 South Indian food list")
    st.caption("Values are estimates for the listed standard quantity. Select a food in Today to calculate a different quantity.")
    allfoods=food_df()
    search_food=st.text_input("Find a food",placeholder="Try dosa, rice, chutney, sundal…",key="food_list_search")
    if search_food:
        allfoods=allfoods[allfoods.name.str.contains(search_food,case=False,na=False)]
    st.dataframe(allfoods[["name","category","serving_qty","unit","calories","protein"]].rename(columns={"name":"Food","category":"Category","serving_qty":"Standard quantity","unit":"Unit","calories":"Calories","protein":"Protein (g)"}),use_container_width=True,hide_index=True)
    st.divider()
    st.markdown("#### Add your own saved food")
    with st.form("custom_food_form"):
        custom_name=st.text_input("Food name",placeholder="e.g. homemade ragi dosa")
        c1,c2,c3=st.columns(3)
        category=c1.selectbox("Category",["Breakfast","Lunch","Dinner","Snack","Side dish","Staple","Protein","Fruit","Drink","Other"])
        serving_qty=c2.number_input("Serving quantity",min_value=0.1,value=1.0,step=0.5)
        unit=c3.selectbox("Unit",["piece","bowl","serving","g","ml","glass","cup","tbsp"])
        n1,n2,n3=st.columns(3)
        calories=n1.number_input("Calories",min_value=0.0,value=0.0,step=10.0)
        protein=n2.number_input("Protein (g)",min_value=0.0,value=0.0,step=0.5)
        carbs=n3.number_input("Carbs (g)",min_value=0.0,value=0.0,step=1.0)
        n4,n5=st.columns(2)
        fat=n4.number_input("Fat (g)",min_value=0.0,value=0.0,step=0.5)
        fiber=n5.number_input("Fiber (g)",min_value=0.0,value=0.0,step=0.5)
        save_custom=st.form_submit_button("Save food",use_container_width=True)
    if save_custom:
        if not custom_name.strip() or calories<=0:
            st.error("Enter a food name and calories.")
        else:
            try:
                sb.table("custom_foods").insert({
                    "user_email":user_email,"name":custom_name.strip(),"category":category,
                    "serving_qty":serving_qty,"unit":unit,"calories":calories,
                    "protein":protein,"carbs":carbs,"fat":fat,"fiber":fiber
                }).execute()
                st.success("Saved. It will be available in your food selector.")
                st.rerun()
            except Exception:
                st.error("Could not save this food. It may already exist in your saved list.")
