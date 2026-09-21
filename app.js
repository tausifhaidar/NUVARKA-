const PRODUCTS=[
{id:1,name:"Core Attitude Tee",category:"tshirt",price:599,tag:"CORE",tone:"dark"},
{id:2,name:"Nuvarka Oversized 01",category:"oversized",price:699,tag:"NEW",tone:"light"},
{id:3,name:"Statement Logo Tee",category:"tshirt",price:599,tag:"DROP 01",tone:"mid"},
{id:4,name:"Essential Heavy Tee",category:"tshirt",price:649,tag:"HEAVYWEIGHT",tone:"outline"},
{id:5,name:"Blackout Oversized",category:"oversized",price:749,tag:"LIMITED",tone:"dark"},
{id:6,name:"Nuvarka Type Tee",category:"tshirt",price:599,tag:"GRAPHIC",tone:"light"},
{id:7,name:"Daily Uniform Tee",category:"tshirt",price:549,tag:"EVERYDAY",tone:"mid"},
{id:8,name:"Attitude Oversized",category:"oversized",price:749,tag:"OVERSIZED",tone:"outline"}];

const cart=[];
const grid=document.getElementById("productGrid");
const count=document.getElementById("cartCount");
const panel=document.getElementById("cartPanel");
const overlay=document.getElementById("overlay");
const itemsBox=document.getElementById("cartItems");
const totalBox=document.getElementById("cartTotal");
const money=n=>"₹"+n.toLocaleString("en-IN");

function renderProducts(filter){
  filter=filter||"all";
  const list=PRODUCTS.filter(p=>filter==="all"||p.category===filter);
  grid.innerHTML=list.map(function(p){
    return '<article class="product-card"><div class="product-image"><span class="product-tag">'+p.tag+'</span><div class="mini-shirt '+p.tone+'"></div></div>'+
      '<div class="product-meta"><div><div class="product-name">'+p.name+'</div><div class="product-sub">Heavyweight cotton · Unisex</div></div><div class="price">'+money(p.price)+'</div></div>'+
      '<button class="add-btn" data-add="'+p.id+'">ADD TO CART</button></article>';
  }).join("");
}

function updateCart(){
  count.textContent=cart.reduce((s,i)=>s+i.qty,0);
  if(!cart.length){
    itemsBox.innerHTML='<div class="empty">Your cart is empty.<br>Add something with attitude.</div>';
  }else{
    itemsBox.innerHTML=cart.map(function(i){
      return '<div class="cart-row"><div class="cart-thumb"><div class="tiny-shirt"></div></div><div><strong>'+i.name+'</strong><div class="small">'+money(i.price)+' each</div>'+
      '<div class="qty"><button data-dec="'+i.id+'">−</button><span>'+i.qty+'</span><button data-inc="'+i.id+'">+</button></div></div><strong>'+money(i.price*i.qty)+'</strong></div>';
    }).join("");
  }
  totalBox.textContent=money(cart.reduce((s,i)=>s+i.price*i.qty,0));
}

function openCart(){panel.classList.add("open");overlay.classList.add("open");panel.setAttribute("aria-hidden","false")}
function closeCart(){panel.classList.remove("open");overlay.classList.remove("open");panel.setAttribute("aria-hidden","true")}

function addToCart(id){
  const p=PRODUCTS.find(x=>x.id===id);
  const old=cart.find(x=>x.id===id);
  if(old) old.qty++; else cart.push({id:p.id,name:p.name,price:p.price,qty:1});
  updateCart();openCart();
}

document.addEventListener("click",function(e){
  const add=e.target.closest("[data-add]");
  const inc=e.target.closest("[data-inc]");
  const dec=e.target.closest("[data-dec]");
  const filter=e.target.closest(".filter");
  if(add)addToCart(Number(add.dataset.add));
  if(inc){const i=cart.find(x=>x.id===Number(inc.dataset.inc));if(i)i.qty++;updateCart()}
  if(dec){const i=cart.find(x=>x.id===Number(dec.dataset.dec));if(i)i.qty--;if(i&&i.qty<=0)cart.splice(cart.indexOf(i),1);updateCart()}
  if(filter){document.querySelectorAll(".filter").forEach(function(b){b.classList.remove("active")});filter.classList.add("active");renderProducts(filter.dataset.filter)}
});

document.getElementById("cartBtn").addEventListener("click",openCart);
document.getElementById("closeCart").addEventListener("click",closeCart);
overlay.addEventListener("click",closeCart);

document.getElementById("whatsappBtn").addEventListener("click",function(){
  if(!cart.length){alert("Cart is empty.");return}
  const WHATSAPP_NUMBER="919999999999";
  const lines=cart.map(function(i){return "• "+i.name+" × "+i.qty+" = "+money(i.price*i.qty)});
  const total=money(cart.reduce((s,i)=>s+i.price*i.qty,0));
  const message=encodeURIComponent("Hi NUVARKA! I want to order:\n\n"+lines.join("\n")+"\n\nTotal: "+total+"\n\nPlease confirm size, availability and delivery.");
  window.open("https://wa.me/"+WHATSAPP_NUMBER+"?text="+message,"_blank");
});

document.getElementById("newsletterForm").addEventListener("submit",function(e){
  e.preventDefault();
  const email=document.getElementById("emailInput").value.trim();
  const msg=document.getElementById("newsletterMsg");
  msg.textContent=email?"You're on the list. Welcome to NUVARKA.":"";
  e.target.reset();
});

renderProducts("all");updateCart();