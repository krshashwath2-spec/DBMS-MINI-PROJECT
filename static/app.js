const entityConfig={
 disasters:{label:"Disasters",singular:"disaster",icon:"⌁",description:"Register incidents and track response status.",fields:[
  {key:"disaster_name",label:"Disaster name",required:true},{key:"disaster_type",label:"Disaster type",required:true,options:["Flood","Earthquake","Cyclone","Landslide","Fire","Drought","Other"]},
  {key:"start_date",label:"Start date",type:"date"},{key:"end_date",label:"End date",type:"date"},
  {key:"severity",label:"Severity",options:["Low","Moderate","High","Critical"],default:"Moderate"},{key:"status",label:"Status",options:["Active","Monitoring","Resolved"],default:"Active"},
  {key:"description",label:"Description",type:"textarea",full:true}]},
 affected_areas:{label:"Affected areas",singular:"affected area",icon:"⌖",description:"Map impacted locations and response priority.",fields:[
  {key:"disaster_id",label:"Disaster",type:"disaster"},{key:"area_name",label:"Area name",required:true},{key:"location",label:"Location",required:true},
  {key:"people_affected",label:"People affected",type:"number",default:0},{key:"priority_level",label:"Priority",options:["Low","Medium","High","Critical"],default:"Medium"}]},
 affected_people:{label:"Affected people",singular:"person",icon:"♙",description:"Register residents and their immediate needs.",fields:[
  {key:"area_id",label:"Affected area",type:"area"},{key:"person_name",label:"Full name",required:true},{key:"age",label:"Age",type:"number"},
  {key:"gender",label:"Gender",options:["Not specified","Female","Male","Other"],default:"Not specified"},{key:"contact_no",label:"Contact number"},
  {key:"address",label:"Address"},{key:"need_type",label:"Need type",required:true},{key:"priority",label:"Priority",options:["Low","Medium","High","Critical"],default:"Medium"}]},
 relief_requests:{label:"Relief requests",singular:"relief request",icon:"♧",description:"Track supply and assistance requests from the field.",fields:[
  {key:"area_id",label:"Affected area",type:"area"},{key:"person_id",label:"Person",type:"person"},{key:"request_type",label:"Request type",required:true},
  {key:"resource_id",label:"Resource",type:"resource"},{key:"quantity_needed",label:"Quantity needed",type:"number",default:1},
  {key:"priority",label:"Priority",options:["Low","Medium","High","Critical"],default:"Medium"},{key:"request_date",label:"Request date",type:"date"},
  {key:"status",label:"Status",options:["Pending","Approved","Fulfilled","Rejected"],default:"Pending"},{key:"remarks",label:"Remarks",type:"textarea",full:true}]},
 medical_requests:{label:"Medical requests",singular:"medical request",icon:"✚",description:"Record medical needs, urgency and assignment.",fields:[
  {key:"person_id",label:"Person",type:"person"},{key:"medical_issue",label:"Medical issue",required:true},{key:"priority",label:"Priority",options:["Low","Medium","High","Critical"],default:"Medium"},
  {key:"request_date",label:"Request date",type:"date"},{key:"status",label:"Status",options:["Pending","Assigned","Completed"],default:"Pending"},
  {key:"assigned_to",label:"Assigned to"},{key:"notes",label:"Notes",type:"textarea",full:true}]},
 shelters:{label:"Shelters",singular:"shelter",icon:"⌂",description:"Monitor shelter locations and available capacity.",fields:[
  {key:"shelter_name",label:"Shelter name",required:true},{key:"location",label:"Location",required:true},{key:"capacity",label:"Capacity",type:"number",required:true,default:0},
  {key:"current_occupancy",label:"Current occupancy",type:"number",default:0},{key:"shelter_type",label:"Shelter type",default:"Relief shelter"},
  {key:"contact_no",label:"Contact number"},{key:"status",label:"Status",options:["Open","Full","Closed"],default:"Open"}]},
 shelter_allocations:{label:"Shelter allocations",singular:"shelter allocation",icon:"↗",description:"Assign people to shelters and track their stay.",fields:[
  {key:"person_id",label:"Person",type:"person",required:true},{key:"shelter_id",label:"Shelter",type:"shelter",required:true},
  {key:"allocation_date",label:"Allocation date",type:"date"},{key:"status",label:"Status",options:["Active","Released"],default:"Active"},
  {key:"remarks",label:"Remarks",type:"textarea",full:true}]},
 resources:{label:"Resources",singular:"resource",icon:"▤",description:"Maintain a catalogue of relief resource types.",fields:[
  {key:"resource_name",label:"Resource name",required:true},{key:"resource_type",label:"Resource type",required:true,options:["Food","Water","Medical","Clothing","Equipment","Transport","Other"]},
  {key:"unit",label:"Unit",default:"units"}]},
 inventory:{label:"Inventory",singular:"inventory item",icon:"▦",description:"Track resource stock and storage locations.",fields:[
  {key:"resource_id",label:"Resource",type:"resource",required:true},{key:"quantity_available",label:"Quantity available",type:"number",required:true,default:0},
  {key:"last_updated",label:"Last updated",type:"datetime-local"},{key:"location",label:"Storage location"}]},
 supply_distributions:{label:"Supply distributions",singular:"supply distribution",icon:"⇢",description:"Record deliveries to a shelter or affected area.",fields:[
  {key:"resource_id",label:"Resource",type:"resource",required:true},{key:"to_shelter_id",label:"Deliver to shelter",type:"shelter"},
  {key:"to_area_id",label:"Deliver to affected area",type:"area"},{key:"quantity_distributed",label:"Quantity",type:"number",required:true},
  {key:"distribution_date",label:"Distribution date",type:"date"},{key:"distributed_by",label:"Distributed by"},
  {key:"remarks",label:"Remarks",type:"textarea",full:true}]},
 rescue_teams:{label:"Rescue teams",singular:"rescue team",icon:"⚑",description:"Coordinate response teams and deployment readiness.",fields:[
  {key:"team_name",label:"Team name",required:true},{key:"team_type",label:"Team type",required:true},
  {key:"team_leader",label:"Team leader"},{key:"contact_no",label:"Contact number"},
  {key:"status",label:"Status",options:["Available","Deployed","Unavailable"],default:"Available"}]},
 vehicles:{label:"Vehicles",singular:"vehicle",icon:"▰",description:"Track response vehicles, teams and field locations.",fields:[
  {key:"team_id",label:"Assigned team",type:"team"},{key:"vehicle_type",label:"Vehicle type",required:true},
  {key:"registration_no",label:"Registration number",required:true},{key:"capacity",label:"Capacity",type:"number",default:1},
  {key:"status",label:"Status",options:["Available","In use","Maintenance"],default:"Available"},{key:"current_location",label:"Current location"}]}
};
const columns={
 disasters:[["disaster_name","Disaster"],["disaster_type","Type"],["severity","Severity"],["status","Status"],["start_date","Start date"]],
 affected_areas:[["area_name","Area"],["disaster_id","Disaster"],["location","Location"],["people_affected","People"],["priority_level","Priority"]],
 affected_people:[["person_name","Person"],["area_id","Affected area"],["age","Age"],["contact_no","Contact"],["need_type","Need"],["priority","Priority"]],
 relief_requests:[["request_type","Request"],["area_id","Area"],["person_id","Person"],["resource_id","Resource"],["quantity_needed","Quantity"],["priority","Priority"],["status","Status"]],
 medical_requests:[["person_id","Person"],["medical_issue","Medical issue"],["priority","Priority"],["request_date","Date"],["status","Status"],["assigned_to","Assigned to"]],
 shelters:[["shelter_name","Shelter"],["location","Location"],["capacity","Capacity"],["current_occupancy","Occupancy"],["shelter_type","Type"],["status","Status"]],
 shelter_allocations:[["person_id","Person"],["shelter_id","Shelter"],["allocation_date","Date"],["status","Status"]],
 resources:[["resource_name","Resource"],["resource_type","Type"],["unit","Unit"]],
 inventory:[["resource_id","Resource"],["quantity_available","Available"],["unit","Unit"],["location","Location"],["last_updated","Updated"]],
 supply_distributions:[["resource_id","Resource"],["to_shelter_id","Shelter"],["to_area_id","Area"],["quantity_distributed","Quantity"],["distribution_date","Date"],["distributed_by","Distributed by"]],
 rescue_teams:[["team_name","Team"],["team_type","Type"],["team_leader","Team leader"],["contact_no","Contact"],["status","Status"]],
 vehicles:[["vehicle_type","Vehicle"],["registration_no","Registration"],["team_id","Assigned team"],["capacity","Capacity"],["status","Status"],["current_location","Location"]]
};
const lookups={
 disaster:["disasters","disaster_id","disaster_name"],area:["affected_areas","area_id","area_name"],person:["affected_people","person_id","person_name"],
 resource:["resources","resource_id","resource_name"],shelter:["shelters","shelter_id","shelter_name"],team:["rescue_teams","team_id","team_name"]
};
const content=document.querySelector("#content");
let activeView="dashboard",lookupCache={},currentUser=null;
const esc=value=>String(value??"—").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const formatReportDate=value=>{const parsed=new Date(value);return Number.isNaN(parsed.getTime())?String(value||"—"):new Intl.DateTimeFormat("en-IN",{timeZone:"Asia/Kolkata",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit",hour12:false}).format(parsed)};
const nice=value=>String(value||"").replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase());
const toast=(message,error=false)=>{const node=document.querySelector("#toast");node.textContent=message;node.className=`toast show${error?" error":""}`;setTimeout(()=>node.classList.remove("show"),3000)};
async function api(url,options={}){const response=await fetch(url,{headers:{"Content-Type":"application/json"},...options});const data=await response.json().catch(()=>({error:"The server returned an invalid response."}));if(response.status===401&&!url.endsWith("/auth/me")&&!url.endsWith("/auth/login")){currentUser=null;renderLogin("Your session expired. Please sign in again.")}if(!response.ok)throw new Error(data.error||"Request failed.");return data}
function setUser(user){currentUser=user;const label=document.querySelector("#current-user"),logout=document.querySelector("#logout-button"),avatar=document.querySelector("#avatar"),usersNav=document.querySelector("#users-nav");label.hidden=!user;logout.hidden=!user;avatar.hidden=Boolean(user);usersNav.hidden=user?.role!=="Administrator";if(user)label.textContent=`${user.email} · ${user.role}`}
function setNav(view){activeView=view;document.querySelectorAll(".nav-item").forEach(button=>button.classList.toggle("active",button.dataset.view===view));document.querySelector("#breadcrumb-current").textContent=view==="dashboard"?"Overview":view==="field_reports"?"Field reports":view==="users"?"User accounts":entityConfig[view].label}
function pageHeader(kicker,title,subtitle,button=""){return `<div class="heading-row"><div><p class="eyebrow">${kicker}</p><h1 class="page-title">${title}</h1><p class="subtitle">${subtitle}</p></div>${button?`<button class="primary-btn" id="heading-action">＋ ${button}</button>`:""}</div>`}
async function loadView(view=activeView){if(!currentUser)return renderLogin();setNav(view);if(view==="dashboard")return renderDashboard();if(view==="field_reports")return renderFieldReports();if(view==="users")return renderUsers();return renderEntity(view)}
function renderLogin(message=""){
 setUser(null);document.querySelectorAll(".nav-item").forEach(button=>button.classList.remove("active"));
 content.innerHTML=`<section class="login-panel"><div class="login-brand"><span class="brand-icon">R</span><div><h1>Sign in to ReliefFlow</h1><p>Use your response-center email and password.</p></div></div>${message?`<div class="error-banner">${esc(message)}</div>`:""}<form id="login-form" class="login-form"><label>Email address<input class="form-control" name="email" type="email" autocomplete="email" required autofocus></label><label>Password<input class="form-control" name="password" type="password" autocomplete="current-password" required></label><button class="primary-btn">Sign in</button></form><div class="auth-links"><button type="button" class="text-btn" id="create-account">Create account</button><button type="button" class="text-btn" id="forgot-password">Forgot password?</button></div><div id="password-help" class="password-help" hidden></div><p class="field-hint">The first account created is Administrator. New accounts are Coordinators.</p></section>`;
 document.querySelector("#login-form").addEventListener("submit",async event=>{event.preventDefault();const button=event.currentTarget.querySelector("button");button.disabled=true;const values=Object.fromEntries(new FormData(event.currentTarget).entries());try{const result=await api("/api/auth/login",{method:"POST",body:JSON.stringify(values)});setUser(result.user);toast(`Signed in as ${result.user.role}.`);await loadView("dashboard")}catch(error){renderLogin(error.message)}});
 document.querySelector("#create-account").addEventListener("click",()=>renderRegister());
 document.querySelector("#forgot-password").addEventListener("click",()=>{const help=document.querySelector("#password-help");help.hidden=false;help.innerHTML=`<b>Password recovery</b><p>For security, password resets are handled by your Administrator. Contact them to reset your Coordinator account.</p><p>If you forgot the Administrator password, run this command in the project folder and replace <code>EMAIL</code> with your login email:</p><code>py -3 app.py --reset-password EMAIL</code><p>The command asks for a new password and signs out existing sessions.</p>`});
}
function renderRegister(message=""){
 content.innerHTML=`<section class="login-panel"><div class="login-brand"><span class="brand-icon">R</span><div><h1>Create a ReliefFlow account</h1><p>Enter your email and choose a password with at least 12 characters.</p></div></div>${message?`<div class="error-banner">${esc(message)}</div>`:""}<form id="register-form" class="login-form"><label>Email address<input class="form-control" name="email" type="email" maxlength="254" autocomplete="email" required autofocus></label><label>Password<input class="form-control" name="password" type="password" minlength="12" maxlength="256" autocomplete="new-password" required></label><label>Confirm password<input class="form-control" name="confirm_password" type="password" minlength="12" autocomplete="new-password" required></label><button class="primary-btn">Create account</button></form><button type="button" class="text-btn" id="back-to-login">Back to sign in</button><p class="field-hint">The first account becomes Administrator. All accounts created after that are Coordinators.</p></section>`;
 document.querySelector("#back-to-login").addEventListener("click",()=>renderLogin());
 document.querySelector("#register-form").addEventListener("submit",async event=>{event.preventDefault();const values=Object.fromEntries(new FormData(event.currentTarget).entries());if(values.password!==values.confirm_password){renderRegister("The passwords do not match.");return}delete values.confirm_password;const button=event.currentTarget.querySelector("button");button.disabled=true;try{const result=await api("/api/auth/register",{method:"POST",body:JSON.stringify(values)});setUser(result.user);toast(`Account created. Signed in as ${result.user.role}.`);await loadView("dashboard")}catch(error){renderRegister(error.message)}});
}
async function signOut(){try{await api("/api/auth/logout",{method:"POST",body:"{}"})}catch(error){toast(error.message,true)}setUser(null);renderLogin("You have signed out.")}
async function renderDashboard(){
 content.innerHTML=`${pageHeader("FIELD OPERATIONS","Response overview","A live snapshot of incidents, people and relief activity.")}
 <div class="metric-grid" id="metrics"><div class="loading">Loading response data…</div></div>
 <section class="panel emergency-panel"><div class="panel-heading"><div><h2 class="panel-title">Emergency contacts · India</h2><div class="panel-caption">For emergencies, call the relevant service directly.</div></div></div><div class="emergency-grid">
 <a class="emergency-contact" href="tel:112"><span class="emergency-service">National emergency</span><strong class="emergency-number">112</strong><span class="emergency-action">Call emergency services</span></a>
 <a class="emergency-contact" href="tel:108"><span class="emergency-service">Ambulance</span><strong class="emergency-number">108</strong><span class="emergency-action">Call ambulance</span></a>
 <a class="emergency-contact" href="tel:101"><span class="emergency-service">Fire services</span><strong class="emergency-number">101</strong><span class="emergency-action">Call fire services</span></a>
 </div><a class="relief-contact-alert" href="tel:656565" aria-label="Call Relief Team emergency contact at 656565"><span class="alert-dot" aria-hidden="true"></span><span class="relief-contact-marquee"><span>RELIEF TEAM EMERGENCY CONTACT · CALL 656565</span></span></a><p class="emergency-note">Tap a number on your phone to call. Confirm service availability in your area; in an emergency, use 112.</p></section>
 <div class="dashboard-grid"><section class="panel"><div class="panel-heading"><div><h2 class="panel-title">Recent disasters</h2><div class="panel-caption">Latest reported incident activity</div></div><button class="secondary-btn" data-go="disasters">View all</button></div><div class="disaster-list" id="recent-disasters"></div></section>
 <section class="panel"><div class="panel-heading"><div><h2 class="panel-title">Quick actions</h2><div class="panel-caption">Add a response record</div></div></div><div class="quick-grid">${Object.entries(entityConfig).map(([key,item])=>`<button class="quick-link" data-add="${key}"><span class="quick-symbol">${item.icon}</span>Add ${item.singular}</button>`).join("")}</div></section></div>
 <section class="panel" style="margin-top:15px"><div class="panel-heading"><div><h2 class="panel-title">Priority relief requests</h2><div class="panel-caption">Requests sorted by urgency</div></div><button class="secondary-btn" data-go="relief_requests">Manage requests</button></div><div id="urgent-requests"></div></section>`;
 try{
  const data=await api("/api/dashboard");lookupCache.disasters=await api("/api/disasters");
  const cards=[["Active disasters",data.metrics.active_disasters,"Incidents not yet resolved","⌁","tone-red"],["Affected people",data.metrics.affected_people,"Residents in the register","♙","tone-blue"],["Pending relief",data.metrics.pending_relief,"Requests awaiting fulfillment","⇢","tone-amber"],["Available shelter spaces",data.metrics.available_shelter_spaces,"Open shelter capacity remaining","⌂","tone-green"]];
  document.querySelector("#metrics").innerHTML=cards.map(([label,value,note,icon,tone])=>`<article class="metric-card"><div class="metric-head">${label}<span class="metric-icon ${tone}">${icon}</span></div><div class="metric-value">${Number(value).toLocaleString()}</div><div class="metric-note">${note}</div></article>`).join("");
  document.querySelector("#recent-disasters").innerHTML=data.disasters.length?data.disasters.map(d=>`<div class="disaster-row"><i class="severity-dot ${esc(d.severity).toLowerCase()}"></i><div><div class="item-name">${esc(d.disaster_name)}</div><div class="item-sub">${esc(d.disaster_type)} · ${esc(d.people_count)} people · ${esc(d.area_count)} areas · ${esc(d.start_date)}</div></div><span class="status-pill ${esc(d.status).toLowerCase()}">${esc(d.status)}</span></div>`).join(""):`<div class="empty-state">No incidents recorded yet.</div>`;
  document.querySelector("#urgent-requests").innerHTML=data.urgent_requests.length?`<div class="table-wrap"><table><thead><tr><th>Request</th><th>Person / area</th><th>Quantity</th><th>Priority</th><th>Status</th></tr></thead><tbody>${data.urgent_requests.map(r=>`<tr><td>${esc(r.request_type)}</td><td>${esc(r.person_name||r.area_name||"Unassigned")}</td><td>${esc(r.quantity_needed)}</td><td><span class="status-pill ${esc(r.priority).toLowerCase()}">${esc(r.priority)}</span></td><td>${esc(r.status)}</td></tr>`).join("")}</tbody></table></div>`:`<div class="empty-state">No relief requests have been logged.</div>`;
 }catch(error){document.querySelector("#metrics").innerHTML=`<div class="error-banner">${esc(error.message)} Check that the local server is running.</div>`}
}
async function getLookups(){const entries=await Promise.all(Object.entries(lookups).map(async([key,[path]])=>[key,await api(`/api/${path}`)]));lookupCache=Object.fromEntries(entries)}
async function renderUsers(){
 if(currentUser?.role!=="Administrator"){toast("Administrator role required to manage users.",true);return loadView("dashboard")}
 content.innerHTML=`${pageHeader("ACCESS CONTROL","User accounts","Create administrator and coordinator accounts.")}<div class="dashboard-grid"><section class="panel"><div class="panel-heading"><div><h2 class="panel-title">Create account</h2><div class="panel-caption">Passwords must contain at least 12 characters.</div></div></div><form id="user-form" class="user-form"><label>Email address<input class="form-control" name="email" type="email" maxlength="254" required></label><label>Temporary password<input class="form-control" name="password" type="password" minlength="12" required autocomplete="new-password"></label><label>Role<select class="form-control" name="role"><option>Coordinator</option><option>Administrator</option></select></label><button class="primary-btn">Create account</button></form></section><section class="panel"><div class="panel-heading"><div><h2 class="panel-title">Role permissions</h2></div></div><p class="role-description"><b>Administrator:</b> manage all records and create user accounts.</p><p class="role-description"><b>Coordinator:</b> view, add, and edit operational records; cannot delete records or manage accounts.</p><p class="field-hint">Permissions are checked by the Python API against each account’s database role.</p></section></div><section class="table-panel user-table"><div class="table-top"><span class="table-title">Registered accounts</span></div><div class="table-wrap" id="users-container"><div class="loading">Loading users…</div></div></section>`;
 try{
  const users=await api("/api/users");
  document.querySelector("#users-container").innerHTML=users.length?`<table><thead><tr><th>Email</th><th>Role</th><th>Status</th><th>Created</th><th>Actions</th></tr></thead><tbody>${users.map(user=>`<tr><td>${esc(user.email)}</td><td>${esc(user.role)}</td><td>${user.is_active?"Active":"Disabled"}</td><td>${esc(user.created_at)}</td><td>${user.user_id===currentUser.user_id?"Current account":`<button class="icon-btn" data-reset-password="${user.user_id}">Reset password</button>`}</td></tr>`).join("")}</tbody></table>`:`<div class="empty-state">No accounts found.</div>`;
  document.querySelectorAll("[data-reset-password]").forEach(button=>button.addEventListener("click",()=>openPasswordReset(users.find(user=>String(user.user_id)===button.dataset.resetPassword))));
  document.querySelector("#user-form").addEventListener("submit",async event=>{event.preventDefault();const button=event.currentTarget.querySelector("button");button.disabled=true;const values=Object.fromEntries(new FormData(event.currentTarget).entries());try{await api("/api/users",{method:"POST",body:JSON.stringify(values)});toast("User account created.");await renderUsers()}catch(error){toast(error.message,true);button.disabled=false}});
 }catch(error){document.querySelector("#users-container").innerHTML=`<div class="error-banner">${esc(error.message)}</div>`}
}
function openPasswordReset(user){
 if(!user)return;
 document.querySelector("#modal-root").innerHTML=`<div class="modal-backdrop"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><div class="modal-header"><h2 id="modal-title">Reset password for ${esc(user.email)}</h2><button class="modal-close" aria-label="Close dialog">×</button></div><form class="modal-form" id="password-reset-form"><div class="form-field"><label>New temporary password (at least 12 characters)</label><input class="form-control" name="password" type="password" minlength="12" maxlength="256" autocomplete="new-password" required></div><div class="form-actions"><button type="button" class="secondary-btn cancel-modal">Cancel</button><button class="primary-btn">Reset password</button></div></form></section></div>`;
 const close=()=>document.querySelector("#modal-root").innerHTML="";
 document.querySelector(".modal-close").addEventListener("click",close);document.querySelector(".cancel-modal").addEventListener("click",close);
 document.querySelector("#password-reset-form").addEventListener("submit",async event=>{event.preventDefault();const button=event.currentTarget.querySelector("button.primary-btn");button.disabled=true;const password=new FormData(event.currentTarget).get("password");try{await api(`/api/users/${user.user_id}/password`,{method:"PUT",body:JSON.stringify({password})});close();toast(`Password reset for ${user.email}. Tell them the temporary password securely.`);await renderUsers()}catch(error){toast(error.message,true);button.disabled=false}});
}
async function renderEntity(key){
 const config=entityConfig[key];
 const canDelete=currentUser?.role==="Administrator";
 content.innerHTML=`${pageHeader("RESPONSE DIRECTORY",config.label,config.description,`Add ${config.singular}`)}<section class="table-panel"><div class="table-top"><span class="table-title" id="record-count">Loading records…</span><input id="table-search" class="search-input" type="search" placeholder="Search records…" aria-label="Search records"></div><div class="table-wrap" id="table-container"><div class="loading">Loading records…</div></div></section>`;
 document.querySelector("#heading-action").addEventListener("click",()=>openForm(key));
 try{
  const [records]=await Promise.all([api(`/api/${key}`),getLookups()]);
  document.querySelector("#record-count").textContent=`${records.length} ${records.length===1?"record":"records"}`;
  const draw=filter=>{
   const selected=records.filter(row=>Object.values(row).some(value=>String(value??"").toLowerCase().includes(filter.toLowerCase())));
   document.querySelector("#table-container").innerHTML=selected.length?`<table><thead><tr>${columns[key].map(([,label])=>`<th>${label}</th>`).join("")}<th>Actions</th></tr></thead><tbody>${selected.map(row=>`<tr>${columns[key].map(([field])=>`<td>${renderCell(key,field,row[field])}</td>`).join("")}<td><div class="row-actions"><button class="icon-btn" data-edit="${row[primaryKeys[key]]}">Edit</button>${canDelete?`<button class="icon-btn danger-btn" data-delete="${row[primaryKeys[key]]}">Delete</button>`:""}</div></td></tr>`).join("")}</tbody></table>`:`<div class="empty-state">${filter?"No matching records.":"No records yet. Add one to get started."}</div>`;
   document.querySelectorAll("[data-edit]").forEach(button=>button.addEventListener("click",()=>openForm(key,records.find(r=>String(r[primaryKeys[key]])===button.dataset.edit))));
   document.querySelectorAll("[data-delete]").forEach(button=>button.addEventListener("click",()=>deleteRecord(key,button.dataset.delete)));
  };
  draw("");document.querySelector("#table-search").addEventListener("input",event=>draw(event.target.value));
 }catch(error){document.querySelector("#table-container").innerHTML=`<div class="error-banner">${esc(error.message)}</div>`}
}
async function renderFieldReports(){
 const canDelete=currentUser?.role==="Administrator";
 content.innerHTML=`${pageHeader("NOSQL FIELD DATA","Field reports","Flexible incident observations stored in MongoDB.","Add field report")}<section class="table-panel"><div class="table-top"><span class="table-title" id="report-count">Loading reports…</span><input id="report-search" class="search-input" type="search" placeholder="Search reports…" aria-label="Search field reports"></div><div class="table-wrap" id="report-container"><div class="loading">Loading reports…</div></div></section>`;
 document.querySelector("#heading-action").addEventListener("click",()=>openReportForm());
 try{
  const reports=await api("/api/field_reports");
  document.querySelector("#report-count").textContent=`${reports.length} ${reports.length===1?"report":"reports"}`;
  const draw=filter=>{
   const selected=reports.filter(report=>Object.values(report).some(value=>String(typeof value==="object"?JSON.stringify(value):value??"").toLowerCase().includes(filter.toLowerCase())));
   document.querySelector("#report-container").innerHTML=selected.length?`<table><thead><tr><th>Date &amp; time (IST)</th><th>Disaster</th><th>Location</th><th>Report type</th><th>Details</th><th>Reported by</th><th>Status</th><th>Actions</th></tr></thead><tbody>${selected.map(report=>`<tr><td>${esc(formatReportDate(report.reported_at))}</td><td>${esc(report.disaster_name||"—")}</td><td>${esc(report.location)}</td><td>${esc(report.report_type)}</td><td>${esc(report.details.length>100?`${report.details.slice(0,100)}…`:report.details)}</td><td>${esc(report.reported_by||"—")}</td><td><span class="status-pill ${esc(report.status).toLowerCase()}">${esc(report.status)}</span></td><td><div class="row-actions"><button class="icon-btn" data-report-edit="${esc(report._id)}">Edit</button>${canDelete?`<button class="icon-btn danger-btn" data-report-delete="${esc(report._id)}">Delete</button>`:""}</div></td></tr>`).join("")}</tbody></table>`:`<div class="empty-state">${filter?"No matching reports.":"No field reports yet. Add one to get started."}</div>`;
   document.querySelectorAll("[data-report-edit]").forEach(button=>button.addEventListener("click",()=>openReportForm(reports.find(report=>report._id===button.dataset.reportEdit))));
   document.querySelectorAll("[data-report-delete]").forEach(button=>button.addEventListener("click",()=>deleteFieldReport(button.dataset.reportDelete)));
  };
  draw("");document.querySelector("#report-search").addEventListener("input",event=>draw(event.target.value));
 }catch(error){document.querySelector("#report-count").textContent="MongoDB connection required";document.querySelector("#report-container").innerHTML=`<div class="error-banner">${esc(error.message)} Start MongoDB, install the Python requirements, and restart the app.</div>`}
}
function openReportForm(report=null){
 const initialDate=report?.reported_at?String(report.reported_at).replace("Z","").slice(0,16):"";
 document.querySelector("#modal-root").innerHTML=`<div class="modal-backdrop"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><div class="modal-header"><h2 id="modal-title">${report?"Update":"Add"} field report</h2><button class="modal-close" aria-label="Close dialog">×</button></div><form class="modal-form"><div class="form-grid">
 <div class="form-field"><label>Disaster name</label><input class="form-control" name="disaster_name" value="${esc(report?.disaster_name||"")}" placeholder="Optional"></div>
 <div class="form-field"><label>Location *</label><input class="form-control" name="location" value="${esc(report?.location||"")}" required></div>
 <div class="form-field"><label>Report type *</label><input class="form-control" name="report_type" value="${esc(report?.report_type||"")}" placeholder="Road blocked, injury, supply need…" required></div>
 <div class="form-field"><label>Reported by</label><input class="form-control" name="reported_by" value="${esc(report?.reported_by||"")}" placeholder="Volunteer or response team"></div>
 <div class="form-field"><label>Reported at</label><input class="form-control" name="reported_at" type="datetime-local" value="${esc(initialDate)}"></div>
 <div class="form-field"><label>Status</label><select class="form-control" name="status">${["New","Verified","Resolved"].map(status=>`<option ${((report?.status||"New")===status)?"selected":""}>${status}</option>`).join("")}</select></div>
 <div class="form-field full"><label>Details *</label><textarea class="form-control" name="details" rows="3" required>${esc(report?.details||"")}</textarea></div>
 <div class="form-field full"><label>Additional fields (JSON)</label><textarea class="form-control" name="extra_fields" rows="4" placeholder='{"water_level":"2m","people_needing_help":12}'>${esc(JSON.stringify(report?.extra_fields||{},null,2))}</textarea><small class="field-hint">Optional flexible data can vary for each field report. Enter a JSON object.</small></div>
 </div><div class="form-actions"><button type="button" class="secondary-btn cancel-modal">Cancel</button><button class="primary-btn">${report?"Save changes":"Save report"}</button></div></form></section></div>`;
 const close=()=>document.querySelector("#modal-root").innerHTML="";
 document.querySelector(".modal-close").addEventListener("click",close);document.querySelector(".cancel-modal").addEventListener("click",close);
 document.querySelector(".modal-backdrop").addEventListener("click",event=>{if(event.target.classList.contains("modal-backdrop"))close()});
 document.querySelector(".modal-form").addEventListener("submit",async event=>{
  event.preventDefault();const payload=Object.fromEntries(new FormData(event.currentTarget).entries());
  try{payload.extra_fields=JSON.parse(payload.extra_fields||"{}");if(payload.reported_at)payload.reported_at=new Date(payload.reported_at).toISOString();else delete payload.reported_at}
  catch(error){toast(error instanceof SyntaxError?"Additional fields must be valid JSON.":error.message,true);return}
  try{await api(`/api/field_reports${report?`/${encodeURIComponent(report._id)}`:""}`,{method:report?"PUT":"POST",body:JSON.stringify(payload)});close();toast(`Field report ${report?"updated":"added"}.`);await loadView("field_reports")}
  catch(error){toast(error.message,true)}
 });
}
async function deleteFieldReport(id){if(!window.confirm("Delete this field report? This action cannot be undone."))return;try{await api(`/api/field_reports/${encodeURIComponent(id)}`,{method:"DELETE"});toast("Field report deleted.");await loadView("field_reports")}catch(error){toast(error.message,true)}}
const primaryKeys={disasters:"disaster_id",affected_areas:"area_id",affected_people:"person_id",relief_requests:"request_id",medical_requests:"medical_req_id",shelters:"shelter_id",shelter_allocations:"allocation_id",resources:"resource_id",inventory:"inventory_id",supply_distributions:"distribution_id",rescue_teams:"team_id",vehicles:"vehicle_id"};
function renderCell(entity,field,value){
 if(field==="resource_id"){const row=lookupCache.resource?.find(r=>r.resource_id===value);return esc(row?.resource_name||`#${value||"—"}`)}
 if(field==="area_id"||field==="to_area_id"){const row=lookupCache.area?.find(r=>r.area_id===value);return esc(row?.area_name||`#${value||"—"}`)}
 if(field==="person_id"){const row=lookupCache.person?.find(r=>r.person_id===value);return esc(row?.person_name||`#${value||"—"}`)}
 if(field==="disaster_id"){const row=lookupCache.disaster?.find(r=>r.disaster_id===value);return esc(row?.disaster_name||`#${value||"—"}`)}
 if(field==="shelter_id"||field==="to_shelter_id"){const row=lookupCache.shelter?.find(r=>r.shelter_id===value);return esc(row?.shelter_name||`#${value||"—"}`)}
 if(field==="team_id"){const row=lookupCache.team?.find(r=>r.team_id===value);return esc(row?.team_name||`#${value||"—"}`)}
 if(field==="status"||field==="severity"||field==="priority"||field==="priority_level")return `<span class="status-pill ${esc(value).toLowerCase().replace(/\s/g,"-")}">${esc(value)}</span>`;
 return esc(value)
}
function openForm(key,record=null){
 const config=entityConfig[key];
 const fields=config.fields.map(field=>{
  const value=record?.[field.key]??field.default??"";
  let control;
  if(lookups[field.type]){
   const [path,id,label]=lookups[field.type],items=lookupCache[field.type]||[];
   const selected=items.find(row=>String(row[id])===String(value));
   const listId=`lookup-${field.type}-${field.key}`;
   control=`<input class="form-control" name="${field.key}" type="text" list="${listId}"
    value="${esc(selected?.[label]||"")}" placeholder="${esc(items.length?`Choose or type ${field.label.toLowerCase()}`:`Type a new ${field.label.toLowerCase()}`)}"
    autocomplete="off" ${field.required?"required":""}>
    <datalist id="${listId}">${items.map(row=>`<option value="${esc(row[label])}"></option>`).join("")}</datalist>
    <small class="field-hint">Choose an existing entry or type a new one. New entries are saved with this form.</small>`;
  }else if(field.options){
   control=`<select class="form-control" name="${field.key}">${field.options.map(option=>`<option ${value===option?"selected":""}>${esc(option)}</option>`).join("")}</select>`;
  }else if(field.type==="textarea")control=`<textarea class="form-control" name="${field.key}" rows="3">${esc(value)}</textarea>`;
  else{const type=field.type||"text";const display=type==="datetime-local"?String(value).replace(" ","T").slice(0,16):value;control=`<input class="form-control" name="${field.key}" type="${type}" value="${esc(display)}" ${field.required?"required":""} ${type==="number"?"min=\"0\"":""}>`}
  return `<div class="form-field ${field.full?"full":""}"><label>${esc(field.label)}${field.required?" *":""}</label>${control}</div>`;
 }).join("");
 document.querySelector("#modal-root").innerHTML=`<div class="modal-backdrop"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><div class="modal-header"><h2 id="modal-title">${record?"Update":"Add"} ${esc(config.singular)}</h2><button class="modal-close" aria-label="Close dialog">×</button></div><form class="modal-form"><div class="form-grid">${fields}</div><div class="form-actions"><button type="button" class="secondary-btn cancel-modal">Cancel</button><button class="primary-btn">${record?"Save changes":"Save record"}</button></div></form></section></div>`;
 const close=()=>document.querySelector("#modal-root").innerHTML="";
 document.querySelector(".modal-close").addEventListener("click",close);document.querySelector(".cancel-modal").addEventListener("click",close);
 document.querySelector(".modal-backdrop").addEventListener("click",event=>{if(event.target.classList.contains("modal-backdrop"))close()});
 document.querySelector(".modal-form").addEventListener("submit",async event=>{
  event.preventDefault();const payload=Object.fromEntries(new FormData(event.currentTarget).entries());
  for(const field of config.fields){if(field.type==="number"&&payload[field.key]!=="")payload[field.key]=Number(payload[field.key]);if(field.type==="datetime-local"&&payload[field.key])payload[field.key]=payload[field.key].replace("T"," ")}
  try{const id=record?.[primaryKeys[key]];await api(`/api/${key}${id?`/${id}`:""}`,{method:record?"PUT":"POST",body:JSON.stringify(payload)});close();toast(`${nice(config.singular)} ${record?"updated":"added"}.`);await loadView(activeView)}
  catch(error){toast(error.message,true)}
 });
}
async function deleteRecord(key,id){if(!window.confirm("Delete this record? This action cannot be undone."))return;try{await api(`/api/${key}/${id}`,{method:"DELETE"});toast("Record deleted.");await loadView(activeView)}catch(error){toast(error.message,true)}}
document.querySelector("#navigation").addEventListener("click",event=>{const button=event.target.closest("[data-view]");if(button)loadView(button.dataset.view)});
document.querySelector("#content").addEventListener("click",event=>{const go=event.target.closest("[data-go]");if(go)loadView(go.dataset.go);const add=event.target.closest("[data-add]");if(add)getLookups().then(()=>openForm(add.dataset.add)).catch(error=>toast(error.message,true))});
document.querySelector("#logout-button").addEventListener("click",signOut);
async function initializeApp(){try{const result=await api("/api/auth/me");setUser(result.user);await loadView("dashboard")}catch(error){renderLogin(error.message==="Please sign in to continue."?"":error.message)}}
initializeApp();
