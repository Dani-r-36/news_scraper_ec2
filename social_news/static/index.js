window.onload = async function load() {
  getStories()
}

async function getStories() {
  const res = await fetch(
    'http://c7-dani-balancer-1986130919.eu-west-2.elb.amazonaws.com/stories',
    {
      method: 'GET',
      credentials: 'include'
    }
  )
  const data = await res.json()

  displayStories(data.stories)
}

async function handleVote(e) {
  const elemID = e.target.id.split('-')
  const id = elemID[0]
  const direction = elemID[1]
  const rawRes = await fetch(
    `http://c7-dani-balancer-1986130919.eu-west-2.elb.amazonaws.com/votes`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ direction }),
      credentials: 'include'
    }
  )
  const res = await rawRes.json()
  location.reload()
}

function displayStories(stories) {
  stories.forEach(createStory) //for each story we add the dynamic text below
}

function createStory(story) {
  const stories = document.getElementById('stories')
  const storyWrapper = document.createElement('div') // what ever in storyRapper, is assigned to html but as a dynamic "text" so changes.
  let point = 'points'
  if (story.score == 1) {
    point = 'point'
  }
  storyWrapper.innerHTML = `
	<p>
		<a class="title" href=${story.url}>${story.title} </a>
		<span>(${story.score} ${point})</span>

	</p>`

  const upvoteButton = createVoteButton('upvote', `${story.id}-up`, '⬆')
  const downvoteButton = createVoteButton('downvote', `${story.id}-down`, '⬇')

  storyWrapper.append(upvoteButton, downvoteButton)
  stories.append(storyWrapper)
}

function createVoteButton(className, id, text) {
  const button = document.createElement('button') //creates a dynamic element for item next to button (think it is #votes)
  button.id = id
  button.className = className
  button.addEventListener('click', handleVote) //calls handleVote function when the click is pressed
  button.innerText = text
  return button
}
