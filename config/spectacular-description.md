Welcome to the Blog app API documentation. Here you can find information about the available endpoints and how to use them.\
**Project page on** [Github]()\
**Contact me:** [Telegram](https://t.me/gspvk)

## API Limitations
- 100 anonymous requests per day

## Auth
To access the secured endpoints, you need to authenticate yourself using a valid JWT token.

The token is valid for 1 month and needs to be refreshed via the `/api/auth/jwt/refresh/` endpoint.\
The refresh token is valid for 1 year and is provided together with the authorization token in the header.