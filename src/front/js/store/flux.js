const apiUrl = process.env.BACKEND_URL
const getState = ({ getStore, getActions, setStore }) => {
	return {
		store: {
			message: null,
			demo: [
				{
					title: "FIRST",
					background: "white",
					initial: "white"
				},
				{
					title: "SECOND",
					background: "white",
					initial: "white"
				}
			]
		},
		actions: {
			// Use getActions to call a function within a fuction
			exampleFunction: () => {
				getActions().changeColor(0, "green");
			},
			userLogin: async (email,password)=>{
				const resp = await getActions().apiFetch("/login", "POST", {email,password})
				console.log({email,password})
				if (resp.code >= 400) {
					return resp
				}
				setStore({accessToken:resp.data.accessToken})
				localStorage.setItem("accessToken", resp.data.accessToken)
				return resp
			},
			loadToken(){
				let token = localStorage.getItem("accessToken")
				setStore({accessToken:token})
			},
			getMessage: async () => {
				try{
					// fetching data from the backend
					const resp = await getActions().apiFetch("/hello")
					setStore({ message: resp.data.message })
					// don't forget to return something, that is how the async resolves
					// return data;
				}catch(error){
					console.log("Error loading message from backend", error)
				}
			},
			changeColor: (index, color) => {
				//get the store
				const store = getStore();

				//we have to loop the entire demo array to look for the respective index
				//and change its color
				const demo = store.demo.map((elm, i) => {
					if (i === index) elm.background = color;
					return elm;
				});

				//reset the global store
				setStore({ demo: demo });
			},
			apiFetch: async (endpoint,method="GET",body={}) => {
				let resp = await fetch(apiUrl + endpoint, method == "GET" ? undefined :{
					method,
					body: JSON.stringify(body),
					headers:{
						"Content-Type":"application/json"
					}
				})
				if(!resp.ok){
					console.error(`${resp.status}: ${resp.statusText}`)
					return {code:resp.status, error:`${resp.status}: ${resp.statusText}`}
				}
				let data = await resp.json()
				return {code:resp.status, data:data}
			}
		}
	};
};

export default getState;
